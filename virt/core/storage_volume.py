import logging, libvirt, os.path

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
    CREATE_PREALLOC_METADATA = 1

    # resize flags
    RESIZE_ALLOCATE =  1    # force allocation of new size
    RESIZE_DELTA =  2       # size is relative to current
    RESIZE_SHRINK =  4      # allow decrease in capacity

    # wipe algorithms
    WIPE_ALG_ZERO = 0       # 1-pass, all zeroes
    WIPE_ALG_NNSA = 1       # 4-pass NNSA Policy Letter NAP-14.1-C (XVI-8)
    WIPE_ALG_DOD = 2        # 4-pass DoD 5220.22-M section 8-306 procedure
    WIPE_ALG_BSI = 3        # 9-pass method recommended by the German Center of Security in Information Technologies
    WIPE_ALG_GUTMANN = 4    # The canonical 35-pass sequence
    WIPE_ALG_SCHNEIER = 5   # 7-pass method described by Bruce Schneier in "Applied Cryptography" (1996)
    WIPE_ALG_PFITZNER7 = 6  # 7-pass random
    WIPE_ALG_PFITZNER33 = 7 # 33-pass random
    WIPE_ALG_RANDOM = 8     # 1-pass random
    WIPE_ALG_LAST = 9       # last algorithm supported by this version of the libvirt API.

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
        self._drv = connection
        if isinstance(self._drv, basestring):
            self._drv = ConnectionManager(self._drv)
        if isinstance(self._drv, ConnectionManager):
            self._drv = self._drv.connection
        # get libvirt.virStoragePool from virStoragePool
        # TODO: in the future, also handle StoragePool objects
        self._pool = pool
        if isinstance(self._pool, basestring):
            manager = StoragePoolManager(conn_handler)
            self._pool = manager.lookup(self._pool)
        # prefetch list of handlers
        if prefetch:
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

    def _lookupByName(self, name):
        handle = None
        # check if storage pool has already been cached
        if name in self._cache['name']:
            handle = self._cache['name'][name]
        # storage pool not in cache, retrieve and cache it
        else:
            try:
                handle = self._pool.storageVolLookupByName(name)
                key = handle.key()
                path = handle.path()
                where = {'name': name, 'key': key, 'path': path}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                # do not raise an exception here, we put a simple warning
                log.warn(e)
        return handle

    def _lookupByKey(self, key):
        handle = None
        # check if domain has already been cached
        if key in self._cache['key']:
            handle = self._cache['key'][key]
        # domain not in cache, retrieve and cache it
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
        # check if domain has already been cached
        if path in self._cache['path']:
            handle = self._cache['path'][path]
        # domain not in cache, retrieve and cache it
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
            raise StorageVolumeManagerError("Volume '{0}' not found".format(name))
        return volume

    ##########################################################################
    # public methods
    ##########################################################################

    def lookup(self, volume):
        """lookup a volume and return the corresponding libvirt.virStoragePool

        :param connection: either a ``basestring`` with the label of the virStorageVol to find, an instance of a ``StorageVolume``
        :returns: an instance of virStorageVol
        """
        handle = None
        # TODO: move refresh when there is a cache miss of flush
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
            log.warn("Unable to find volume {0} in {1} on {2}", volume, self._pool.name(), self._drv.getURI())
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

    def create(self, volume, flags=0):
        # TODO: enable more input formats ?
        # check if volume already exists
        handle = self.lookup(volume.name)
        if handle:
            raise StorageVolumeManagerError("'{0} already exists.".format(handle.path()))
        # creating new volume
        try:
            volume_xml = volume.unparse()
            # check if 
            allocation = volume.allocation
            if allocation and allocation["#text"] > StorageVolumeManager.MAX_ALLOCATION:
                size = allocation["#text"]
                unit = allocation["@unit"]
                log.warning("Allocation of {0}{1} asked for {2}, only {3} really allocated.".format(size, unit, volume.name, StorageVolumeManager.MAX_ALLOCATION))
            self._pool.createXML(volume_xml, flags)
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
            # extra flags; not used yet, so callers should always pass 0
            origin_xml = origin_volume.XMLDesc(0)
            origin_obj = StorageVolume.parse(origin_xml)
            # clone object and remove key
            clone_obj = origin_obj
            clone_obj.key = None
            clone_obj.name = clone
            # rebuild xml corresponding to clone object and create
            clone_xml = clone_obj.unparse()
            clone_vol = self._pool.createXMLFrom(clone_xml, origin_volume, flags)
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
            volume.resize(capacity, flags)
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
            if algorithm:
                volume.wipePattern(algorithm, flags)
            else:
                volume.wipe(flags)
        except libvirt.libvirtError as e:
            log.exception(e)
            raise StorageVolumeManagerError(e)

    def download(self, volume, filename, offset=0, length=0, flags=0):
        # TODO: enable more formats ?
        if isinstance(volume, StorageVolume):
            volume = self._lookup_volume(volume.name)
        elif isinstance(volume, basestring):
            volume = self._lookup_volume(volume)
        # perform download
        recv_handler = lambda stream, buffer, filedes: filedes.write(buffer)
        try:
            if isinstance(filename, basestring):
                if os.path.exists(filename):
                    raise StorageVolumeManagerError("file {0} already exists".format(filename))
                file = open(filename, 'wb')
            else:
                file = filename
            stream = self._drv.newStream(flags=0)
            # extra flags; not used yet, so callers should always pass 0
            mime = volume.download(stream, offset, length, flags=0)
            stream.recvAll(recv_handler, file)
            stream.finish()
            file.close()
        except (IOError, libvirt.libvirtError) as e:
            stream.abort()
            file.close()
            log.exception(e)
            raise StorageVolumeManagerError(e)

    def upload(self, volume, filename, offset=0, length=0, flags=0):
        # TODO: enable more formats ?
        if isinstance(name, StorageVolume):
            volume = self._lookup_volume(name.name)
        elif isinstance(name, libvirt.virStorageVol):
            volume = name
        else:
            volume = self._lookup_volume(name)
        # perform upload
        send_handler = lambda stream, count, filedes: filedes.read(count)
        try:
            if isinstance(filename, basestring):
                if not os.path.isfile(filename):
                    raise StorageVolumeManagerError("{0} is not a file".format(filename))
                file = open(filename, 'rb')
            else:
                file = filename
            stream = self._drv.newStream(flags=0)
            # extra flags; not used yet, so callers should always pass 0
            mime = volume.upload(stream, offset, length, flags=0)
            stream.sendAll(send_handler, file)
            stream.finish()
            file.close()
        except (IOError, libvirt.libvirtError) as e:
            stream.abort()
            file.close()
            log.exception(e)
            raise StorageVolumeManagerError(e)
