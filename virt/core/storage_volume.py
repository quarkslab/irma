import logging, libvirt, xmltodict

from lib.common import compat
from lib.common.utils import UUID
from lib.common.oopatterns import ParametricSingleton
from lib.virt.core.connection import ConnectionManager
from lib.virt.core.storage_pool import StoragePoolManager
from lib.virt.core.exceptions import StoragePoolManagerError, StorageVolumeManagerError

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
        if isinstance(conn_handler, ConnectionManager):
            conn_handler = conn_handler.connection
        if not isinstance(conn_handler, libvirt.virConnect):
            raise StorageVolumeManagerError("'connection' field type '{0}' is not valid".format(type(conn_handler)))

        if isinstance(pool_handler, basestring):
            poolman = StoragePoolManager(conn_handler)
            pool_handler = poolman.lookup(pool_handler)
        if not isinstance(pool_handler, libvirt.virStoragePool):
            raise StorageVolumeManagerError("'pool' field type '{0}' is not valid".format(type(pool_handler)))

        try:
            uri = conn_handler.getURI()
            pool_name = pool_handler.name()
        except libvirt.libvirtError as e:
            raise DomainManagerError("unable to get domain uri from connection handle")
        return (uri, pool_name)

    ##########################################################################
    # constants
    ##########################################################################

    # Available state
    ACTIVE = 1
    INACTIVE = 2

    # Available status

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, connection, pool, prefetch=False):
        """Instantiate a storage pool manager for specified connection

        :param connection: either an instance of a ``ConnectionManager`` or directly a libvirt connection handler
        :param prefetch: set to True if prefetching storage pool handlers for this connection is required
        :raises: StoragePoolManagerError if ``connection`` is not an expected type or None
        """
        if not connection:
            raise StorageVolumeManagerError("'connection' field value '{0}' is not valid".format(connection))
        elif not isinstance(connection, (libvirt.virConnect, ConnectionManager)):
            raise StorageVolumeManagerError("'connection' field type '{0}' is not valid".format(type(connection)))
        if not pool:
            raise StorageVolumeManagerError("'connection' field value '{0}' is not valid".format(pool))
        elif not isinstance(pool, libvirt.virStoragePool):
            raise StorageVolumeManagerError("'connection' field type '{0}' is not valid".format(type(pool)))

        self._cache = {'name': {}, 'key': {}, 'path': {}}

        self._drv = connection
        if isinstance(self._drv, ConnectionManager):
            self._drv = self._drv.connection
        
        self._pool = pool

        # TODO: implement prefetch
##         if prefetch:
##             pools = self.list()
##             for pool in pools:
##                 self.lookup(pool)

    ##########################################################################
    # context manager stuff
    ##########################################################################

    def __enter__(self):
        return self

    ##########################################################################
    # internal helpers
    ##########################################################################

    def _cache_handle(self, cache, entry, where=None):
        if not isinstance(cache, dict):
            raise ValueError("'cache' fields must be a dict")
        if where and entry:
            for key, value in where.items():
                if key in cache:
                    cache[key][value] = entry

    def _lookupByName(self, name):
        # type checking
        if not isinstance(name, basestring):
            raise StoragePoolManagerError("'name' field type '{0}' is not valid".format(type(name)))

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
                log.error('{0}'.format(e))
        return handle

    def _lookupByKey(self, key):
        # type checking
        if not isinstance(key, basestring) or not UUID.validate(key):
            raise StoragePoolManagerError("'key' field '{0}' is not valid".format(key))

        handle = None
        # check if domain has already been cached
        if key in self._cache['key']:
            handle = self._cache['key'][key]
        # domain not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.storagePoolLookupByUUIDString(key)
                name = handle.name()
                where = {'name': name, 'key': key}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    def _lookupByPath(self, path):
        # type checking
        if not isinstance(path, basestring):
            raise StoragePoolManagerError("'path' field '{0}' is not valid".format(path))

        handle = None
        # check if domain has already been cached
        if path in self._cache['path']:
            handle = self._cache['path'][path]
        # domain not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.storagePoolLookupByUUIDString(path)
                name = handle.name()
                where = {'name': name, 'path': path}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    ##########################################################################
    # public methods
    ##########################################################################

    def lookup(self, volume):
        handle = None
        if isinstance(volume, (tuple, list)):
            handle = list()
            for onevolume in volume:
                handle.append(self.lookup(onevolume))
            handle = tuple(handle)
        elif isinstance(volume, basestring):
            handle = self._lookupByName(volume)
            if not handle:
                handle = self._lookupByKey(volume)
            if not handle:
                handle = self._lookupByPath(volume)
            if not handle:
                log.warn("Unable to find volume {0} in {1} on {2}", volume, self._pool.name(), self._uri)
        return handle

    def list(self):
        """list storage volume for this pool

        :returns: a tuple containing storage volume names
        """
        labels = list()

        try:
            labels.extend(self._pool.listVolumes())
        except libvirt.libvirtError as e:
            log.error('{0}'.format(e))

        return tuple(labels)

    # TODO: add more input types
    # TODO: test clone with a different remote pool
    def clone(self, src, dest):
        if not isinstance(src, basestring):
            raise StoragePoolManagerError("'src' field '{0}' is not valid".format(path))
        if not isinstance(dest, basestring):
            raise StoragePoolManagerError("'dest' field '{0}' is not valid".format(path))

        orig_vol = self.lookup(src)
        if not orig_vol:
            raise StoragePoolManagerError("Unable to find volume '{0}' on '{1}'".format(src, self._pool.name()))
    
        try:
            # extra flags; not used yet, so callers should always pass 0
            orig_xml = orig_vol.XMLDesc(0)
            orig_dict = xmltodict.parse(orig_xml)
        except libvirt.libvirtError as e:
            raise StoragePoolManagerError("Unable to find volume '{0}' on '{1}'".format(src, self._pool.name()))

        # create new volume
        try:
            new_dict = orig_dict
            del new_dict['volume']['key']
            new_dict['volume']['name'] = dest
            new_xml = xmltodict.unparse(new_dict)
            new_vol = self._pool.createXMLFrom(new_xml, orig_vol, 0)
        except KeyError as e:
            raise StoragePoolManagerError("Malformed XML, abort ...")
        except libvirt.libvirtError as e:
            raise StoragePoolManagerError("Unable to create volume '{0}' on '{1}'".format(dest, self._pool.name()))

        # update cache
        return self.lookup(dest)
