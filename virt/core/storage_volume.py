import logging, libvirt, time, os.path

from multiprocessing import Array, Process as Task

from lib.common import compat
from lib.common.utils import UUID
from lib.common.oopatterns import ParametricSingleton
from lib.virt.core.connection import ConnectionManager
from lib.virt.core.storage_pool import StoragePoolManager
from lib.virt.core.mapper.storage_volume import StorageVolume
from lib.virt.core.exceptions import StoragePoolManagerError, StorageVolumeManagerError, StorageVolumeError

log = logging.getLogger(__name__)

class StorageVolumeManager(ParametricSingleton):
    """Storage volume manager to a manage volumes on local or remote storage pool manager"""

    ##########################################################################
    # parametric singleton stuff
    ##########################################################################

    @staticmethod
    def depends_on(cls, *args, **kwargs):
        # singleton is based on the uri and the pool, extracted from the libvirt handler
        (conn_handler, pool_handler) = args[0]
        # get libvirt.virConnect instance from conn_handler
        if isinstance(conn_handler, basestring):
            conn_handler = ConnectionManager(conn_handler)
        if isinstance(conn_handler, ConnectionManager):
            conn_handler = conn_handler.connection
        # TODO: in the future, also handle StoragePool objects
        # get libvirt.virStoragePool instance from pool_handler
        if isinstance(pool_handler, basestring):
            manager = StoragePoolManager(conn_handler)
            pool_handler = manager.lookup(pool_handler)
        # get attribute and add to singleton
        try:
            uri = conn_handler.getURI()
            pool_name = None
            if pool_handler:
                pool_name = pool_handler.name()
        except (AttributeError, libvirt.libvirtError) as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)
        # return keys for parametric singleton
        return (uri, pool_name)

    ##########################################################################
    # constants
    ##########################################################################

    # maximum allocation
    MAX_ALLOCATION = 197632 # determined empirically

    # create/clone flags
    CREATE_PREALLOC_METADATA = 1 # libvirt.VIR_STORAGE_VOL_CREATE_PREALLOC_METADATA is not defined in libvirt.py

    # resize flags
    RESIZE_ALLOCATE = libvirt.VIR_STORAGE_VOL_RESIZE_ALLOCATE # force allocation of new size
    RESIZE_DELTA = libvirt.VIR_STORAGE_VOL_RESIZE_DELTA # size is relative to current
    RESIZE_SHRINK = libvirt.VIR_STORAGE_VOL_RESIZE_SHRINK # allow decrease in capacity

    # wipe algorithms
    WIPE_ALG_ZERO = libvirt.VIR_STORAGE_VOL_WIPE_ALG_ZERO # 1-pass, all zeroes
    WIPE_ALG_NNSA = libvirt.VIR_STORAGE_VOL_WIPE_ALG_NNSA # 4-pass NNSA Policy Letter NAP-14.1-C (XVI-8)
    WIPE_ALG_DOD = libvirt.VIR_STORAGE_VOL_WIPE_ALG_DOD # 4-pass DoD 5220.22-M section 8-306 procedure
    WIPE_ALG_BSI = libvirt.VIR_STORAGE_VOL_WIPE_ALG_BSI # 9-pass method recommended by the German Center of Security in Information Technologies
    WIPE_ALG_GUTMANN = libvirt.VIR_STORAGE_VOL_WIPE_ALG_GUTMANN # The canonical 35-pass sequence
    WIPE_ALG_SCHNEIER = libvirt.VIR_STORAGE_VOL_WIPE_ALG_SCHNEIER # 7-pass method described by Bruce Schneier in "Applied Cryptography" (1996)
    WIPE_ALG_PFITZNER7 = libvirt.VIR_STORAGE_VOL_WIPE_ALG_PFITZNER7 # 7-pass random
    WIPE_ALG_PFITZNER33 = libvirt.VIR_STORAGE_VOL_WIPE_ALG_PFITZNER33 # 33-pass random
    WIPE_ALG_RANDOM = libvirt.VIR_STORAGE_VOL_WIPE_ALG_RANDOM # 1-pass random

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, connection, pool, prefetch=False):
        """Instantiate a storage pool manager for specified connection

        :param connection: either a ``basestring`` from which will be created a connection, an instance of a ``ConnectionManager`` or directly a libvirt connection handler
        :param prefetch: ``True`` if prefetching storage pool handlers for this
connection is required. Set to ``False`` by default
        :raises: StorageVolumeManagerError
        """

        # create handle cache
        self._cache = {'name': {}, 'key': {}, 'path': {}}
        # get libvirt.virConnection from connection
        self._set_drv(connection)
        # get libvirt.virStoragePool from virStoragePool
        # TODO: in the future, also handle StoragePool objects
        self._set_pool(pool)
        if isinstance(self._pool, basestring):
            manager = StoragePoolManager(conn_handler)
            self._pool = manager.lookup(self._pool)
        # prefetch list of handlers
        if self._pool and prefetch:
            # extra flags; not used yet, so callers should always pass 0
            self._pool.refresh(flags=0)
            map(lambda name: self._lookupByName(name), self.list())

    ##########################################################################
    # context manager stuff
    ##########################################################################

    def __enter__(self):
        return self

    ##########################################################################
    # internal helpers
    ##########################################################################

    # TODO: update when new cache pattern will be implemented
    def _cache_handle(self, cache, entry, where):
        if where and entry:
            for key, value in where.items():
                if key in cache:
                    cache[key][value] = entry

    # libvirt.virConnection from connection 
    def _set_drv(self, connection):
        self._drv = connection
        if isinstance(self._drv, basestring):
            self._drv = ConnectionManager(self._drv)
        if isinstance(self._drv, ConnectionManager):
            self._drv = self._drv.connection       

    # libvirt.virStoragePool from virStoragePool
    def _set_pool(self, pool):
        self._pool = pool
        if isinstance(self._pool, basestring):
            manager = StoragePoolManager(self._drv)
            self._pool = manager.lookup(self._pool)
        
    def _update_pool(self, pool):
        opool = getattr(self, "_pool", None)
        self._set_pool(pool)
        # update parametric singleton
        if opool != self._pool:
            drv_uri = self._drv.getURI()
            opool_name = opool
            if isinstance(opool_name, libvirt.virStoragePool):
                opool_name = opool_name.name()
            pool_name = self._pool.name()
            StorageVolumeManager.update_key((drv_uri, opool_name), (drv_uri, pool_name))

    def _lookupByName(self, name):
        handle = None
        # check if storage volume has already been cached
        if name in self._cache['name']:
            handle = self._cache['name'][name]
        # storage volume not in cache, retrieve and cache it
        else:
            if self._pool:
                try:
                    handle = self._pool.storageVolLookupByName(name)
                    key = handle.key()
                    path = handle.path()
                    where = {'name': name, 'key': key, 'path': path}
                    self._cache_handle(self._cache, handle, where)
                except libvirt.libvirtError as e:
                    # do not raise an exception here, we put a simple warning
                    log.warn(e)
            else:
                log.warn("pool is not set, skipping storageVolLookupByName()")
        return handle

    def _lookupByKey(self, key):
        handle = None
        # check if storage volume has already been cached
        if key in self._cache['key']:
            handle = self._cache['key'][key]
        # storage volume not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.storageVolLookupByKey(key)
                name = handle.name()
                path = handle.path()
                where = {'name': name, 'key': key, 'path': path}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                # do not raise an exception here, we put a simple warning
                log.warn(e)
        return handle

    def _lookupByPath(self, path):
        handle = None
        # check if storage volume has already been cached
        if path in self._cache['path']:
            handle = self._cache['path'][path]
        # storage volume not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.storageVolLookupByPath(path)
                name = handle.name()
                key = handle.key()
                where = {'name': name, 'key': key, 'path': path}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                # do not raise an exception here, we put a simple warning
                log.warn(e)
        return handle

    def _lookup_volume(self, name):
        volume = self.lookup(name)
        if not volume:
            e = "Volume '{0}' not found".format(name)
            log.error(e)
            raise StorageVolumeManagerError(e)
        return volume

    ##########################################################################
    # public methods
    ##########################################################################

    pool = property(None, _update_pool)

    def lookup(self, volume):
        """lookup a volume and return the corresponding libvirt.virStoragePool

        :param connection: either a ``basestring`` with the label of the virStorageVol to find, an instance of a ``StorageVolume``
        :returns: an instance of virStorageVol
        """
        handle = None
        # TODO: move refresh when there is a cache miss of flush
        if self._pool:
            self._pool.refresh(flags=0)
        # perform lookup first by name, then by key and finally by path
        if isinstance(volume, basestring):
            handle = self._lookupByName(volume)
            if not handle:
                handle = self._lookupByKey(volume)
            if not handle:
                handle = self._lookupByPath(volume)
        elif isinstance(volume, StorageVolume):
            volume = getattr(volume, 'name', None)
            if volume:
                handle = self._lookupByName(volume)
            volume = getattr(volume, 'key', None)
            if not handle and volume:
                handle = self._lookupByKey(volume)
            volume = getattr(volume, 'path', None)
            if not handle and volume:
                handle = self._lookupByPath(volume)
        # warn if no handle has been found
        if not handle:
            log.warn("Unable to find volume {0} on {1}", volume, self._drv.getURI())
        # return handle
        return handle

    def list(self):
        """list storage volume for this pool

        :returns: a tuple containing storage volume names
        """
        labels = list()
        try:
            labels.extend(self._pool.listVolumes())
        except libvirt.libvirtError as e:
            # do not raise an exception here, we simply log the exception
            log.exception(e)
        return tuple(labels)

    def info(self, volume):
        if isinstance(volume, basestring):
            volume = self._lookup_volume(volume)
        try:
            # extra flags; not used yet, so callers should always pass 0
            xml = volume.XMLDesc(0)
            return StorageVolume.parse(xml)
        except (libvirt.libvirtError, StorageVolumeError) as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)

    def create(self, volume, flags=0):
        # TODO: enable more input formats ?
        # check if volume already exists
        handle = self.lookup(volume.name)
        if handle:
            e = "'{0} already exists.".format(handle.path())
            log.error(e)
            raise StorageVolumeManagerError(e)
        # creating new volume
        try:
            volume_xml = volume.unparse()
            # add a warning for allocation
            allocation = volume.allocation
            if allocation and allocation["#text"] > StorageVolumeManager.MAX_ALLOCATION:
                size = allocation["#text"]
                unit = allocation["@unit"]
                log.warning("allocation of {0}{1} asked for {2}, only {3} really allocated.".format(size, unit, volume.name, StorageVolumeManager.MAX_ALLOCATION))
            # sanitizing flags
            flags = flags & StorageVolumeManager.CREATE_PREALLOC_METADATA
            self._pool.createXML(volume_xml, flags=flags)
        except (libvirt.libvirtError, StorageVolumeError) as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)
        # update cache
        return self.lookup(volume.name)

    def clone(self, origin, clone, flags=0):
        # TODO: enable more formats ?
        # find origin volume
        if isinstance(origin, StorageVolume):
            origin_volume = self._lookup_volume(origin.name)
        elif isinstance(origin, libvirt.virStorageVol):
            origin_volume = origin
        else:
            origin_volume = self._lookup_volume(origin)
        # perform cloning
        try:
            # clone object and remove key
            origin_obj = self.info(origin_volume.name())
            clone_obj = origin_obj
            clone_obj.key = None
            clone_obj.name = clone
            # rebuild xml corresponding to clone object and create
            clone_xml = clone_obj.unparse()
            # sanitizing flags
            flags = flags & StorageVolumeManager.CREATE_PREALLOC_METADATA
            clone_vol = self._pool.createXMLFrom(clone_xml, origin_volume, flags=flags)
        except (libvirt.libvirtError, StorageVolumeError) as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)
        # update cache
        return self.lookup(clone)

    def delete(self, name):
        # TODO: enable more formats ?
        # find volume to delete
        if isinstance(name, StorageVolume):
            volume = self._lookup_volume(name.name)
        elif isinstance(name, libvirt.virStorageVol):
            volume = name
        else:
            volume = self._lookup_volume(name)
        # delete the volume
        try:
            # extra flags; not used yet, so callers should always pass 0
            volume.delete(flags=0)
        except libvirt.libvirtError as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)

    def resize(self, name, capacity, flags=0):
        # TODO: enable more formats ?
        # find volume to resize
        if isinstance(name, StorageVolume):
            volume = self._lookup_volume(name.name)
        elif isinstance(name, libvirt.virStorageVol):
            volume = name
        else:
            volume = self._lookup_volume(name)
        # resize the volume
        try:
            # sanitizing flags
            flags = flags & (StorageVolumeManager.RESIZE_ALLOCATE|StorageVolumeManager.RESIZE_DELTA|StorageVolumeManager.RESIZE_SHRINK)
            volume.resize(capacity, flags=flags)
        except libvirt.libvirtError as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)

    def wipe(self, name, algorithm=None, flags=0):
        # TODO: enable more formats ?
        # find volume to wipe
        if isinstance(name, StorageVolume):
            volume = self._lookup_volume(name.name)
        elif isinstance(name, libvirt.virStorageVol):
            volume = name
        else:
            volume = self._lookup_volume(name)
        # perform volume wipe
        try:
            # future flags, use 0 for now
            flags = flags & 0
            if algorithm:
                # sanitize algorithm
                algorithm = algorithm & (StorageVolumeManager.WIPE_ALG_ZERO|StorageVolumeManager.WIPE_ALG_NNSA|StorageVolumeManager.WIPE_ALG_DOD|StorageVolumeManager.WIPE_ALG_BSI|StorageVolumeManager.WIPE_ALG_GUTMANN|StorageVolumeManager.WIPE_ALG_SCHNEIER|StorageVolumeManager.WIPE_ALG_PFITZNER7|StorageVolumeManager.WIPE_ALG_PFITZNER33|StorageVolumeManager.WIPE_ALG_RANDOM)
                volume.wipePattern(algorithm, flags=flags)
            else:
                volume.wipe(flags=flags)
        except libvirt.libvirtError as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)

    def download(self, volume, filename, offset=0, length=0, flags=0, async=False):

        def _recv_handler(stream, buffer, opaque):
            filedes, status = opaque
            filedes.write(buffer)
            if status:
                status[0] += len(buffer)

        def _download_worker(volume, filename, offset, length, flags, status):
            try:
                if isinstance(filename, basestring):
                    if os.path.exists(filename):
                        e = "file {0} already exists".format(filename)
                        log.error(e)
                        raise StorageVolumeManagerError(e)
                    file = open(filename, 'wb')
                else:
                    file = filename
                stream = self._drv.newStream(flags=0)
                # extra flags; not used yet, so callers should always pass 0
                mime = volume.download(stream, offset, length, flags=0)
                # perform download
                stream.recvAll(_recv_handler, (file, status))
                stream.finish()
                file.close()
            except (IOError, libvirt.libvirtError) as e:
                stream.abort()
                file.close()
                if os.path.exists(filename):
                    os.unlink(filename)
                log.exception(e)
                raise StorageVolumeManagerError(e)

        # TODO: enable more formats ?
        if isinstance(volume, StorageVolume):
            volume = self._lookup_volume(volume.name)
        elif isinstance(volume, basestring):
            volume = self._lookup_volume(volume)
        # determining byte count to download
        bytecount = length
        if not length:
            type, capacity, bytecount = volume.info()
        # creating shared memory to get status
        status = Array('L', [0, bytecount]) if async else None
        task = Task(target=_download_worker, args=(volume, filename, offset, length, flags, status))
        task.start()
        # if not asynchronous, wait for the task to finish
        if async:
            # NOTE: (status[0], status[1]) contain (already copied, total) bytes count
            return task, status
        else:
            task.join()
        
    def upload(self, volume, filename, offset=0, length=0, flags=0, async=False):

        def _send_handler(stream, count, opaque):
            filedes, status = opaque
            data = filedes.read(count)
            if status:
                status[0] += len(data)

        def _upload_worker(volume, filename, offset, length, flags, status):
            try:
                if isinstance(filename, basestring):
                    if not os.path.isfile(filename):
                        e = "{0} is not a file".format(filename)
                        log.error(e)
                        raise StorageVolumeManagerError(e)
                    file = open(filename, 'rb')
                else:
                    file = filename
                stream = self._drv.newStream(flags=0)
                # extra flags; not used yet, so callers should always pass 0
                mime = volume.upload(stream, offset, length, flags=0)
                stream.sendAll(_send_handler, (file, status))
                stream.finish()
                file.close()
            except (IOError, libvirt.libvirtError) as e:
                stream.abort()
                file.close()
                log.exception(e)
                raise StorageVolumeManagerError(e)

        # TODO: enable more formats ?
        if isinstance(name, StorageVolume):
            volume = self._lookup_volume(name.name)
        elif isinstance(name, libvirt.virStorageVol):
            volume = name
        else:
            volume = self._lookup_volume(name)
        # determining byte count to upload
        bytecount = length
        if not length:
            type, capacity, bytecount = volume.info()
        # creating shared memory to get status
        status = Array('L', [0, bytecount]) if async else None
        task = Task(target=_upload_worker, args=(volume, filename, offset, length, flags, status))
        task.start()
        # if not asynchronous, wait for the task to finish
        if async:
            # NOTE: (status[0], status[1]) contain (already copied, total) bytes count
            return task, status
        else:
            task.join()
