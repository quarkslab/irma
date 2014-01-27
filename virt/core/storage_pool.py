import logging, libvirt, xmltodict

from lib.common import compat
from lib.common.utils import UUID
from lib.common.oopatterns import ParametricSingleton
from lib.virt.core.connection import ConnectionManager
from lib.virt.core.exceptions import StoragePoolManagerError

log = logging.getLogger(__name__)

class StoragePoolManager(ParametricSingleton):
    """Storage pool manager to a manage storage on local or remote virtual machine manager"""

    ##########################################################################
    # parametric singleton stuff
    ##########################################################################

    @staticmethod
    def depends_on(cls, *args, **kwargs):
        # singleton is based on the uri, extracted from the libvirt handler
        (handler,) = args[0]
        if isinstance(handler, basestring):
            handler = ConnectionManager(handler)
        if isinstance(handler, ConnectionManager):
            handler = handler.connection
        try:
            uri = handler.getURI()          
        except libvirt.libvirtError as e:
            log.exception(e)
            raise StoragePoolManagerError(e)
        return uri

    ##########################################################################
    # constants
    ##########################################################################

    # Available state
    ACTIVE = 1
    INACTIVE = 2

    # Available status
    POOL_INACTIVE = libvirt.VIR_STORAGE_POOL_INACTIVE
    POOL_BUILDING = libvirt.VIR_STORAGE_POOL_BUILDING
    POOL_RUNNING = libvirt.VIR_STORAGE_POOL_RUNNING
    POOL_DEGRADED = libvirt.VIR_STORAGE_POOL_DEGRADED
    POOL_INACCESSIBLE = libvirt.VIR_STORAGE_POOL_INACCESSIBLE

    # Available delete flags
    DELETE_NORMAL = libvirt.VIR_STORAGE_POOL_DELETE_NORMAL # Delete metadata only (fast)
    DELETE_ZEROED = libvirt.VIR_STORAGE_POOL_DELETE_ZEROED # Clear all data to zeros (slow)
    
    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, connection, prefetch=False):
        """Instantiate a storage pool manager for specified connection

        :param connection: either an instance of a ``ConnectionManager`` or directly a libvirt connection handler
        :param prefetch: set to True if prefetching storage pool handlers for this connection is required
        :raises: StoragePoolManagerError if ``connection`` is not an expected type or None
        """
        # handle cache
        self._cache = {'name': {}, 'uuid': {}}
        # get libvirt.virConnection from connection
        self._set_drv(connection)
        # prefetch list of handlers
        if prefetch:
            map(lambda name: self._lookup(_lookupByName(name)), self.list())

    ##########################################################################
    # context manager stuff
    ##########################################################################

    def __enter__(self):
        return self

    ##########################################################################
    # internal helpers
    ##########################################################################

    # libvirt.virConnection from connection 
    def _set_drv(self, connection):
        self._drv = connection
        if isinstance(self._drv, basestring):
            self._drv = ConnectionManager(self._drv)
        if isinstance(self._drv, ConnectionManager):
            self._drv = self._drv.connection       

    def _list_active(self):
        labels = list()
        try:
            labels.extend(self._drv.listStoragePools())
        except libvirt.libvirtError as e:
            raise StoragePoolManagerError("{0}".format(e))
        return tuple(labels)

    def _list_inactive(self):
        labels = list()
        try:
            labels.extend(self._drv.listDefinedStoragePools())
        except libvirt.libvirtError as e:
            raise StoragePoolManagerError("{0}".format(e))
        return tuple(labels)

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
                handle = self._drv.storagePoolLookupByName(name)
                uuid = handle.UUIDString()
                where = {'name': name, 'uuid': uuid}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    def _lookupByUUID(self, uuid):
        # type checking
        if not isinstance(uuid, basestring) or not UUID.validate(uuid):
            raise StoragePoolManagerError("'uuid' field '{0}' is not valid".format(uuid))

        handle = None
        # check if domain has already been cached
        if uuid in self._cache['uuid']:
            handle = self._cache['uuid'][uuid]
        # domain not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.storagePoolLookupByUUIDString(uuid)
                name = handle.name()
                where = {'name': name, 'uuid': uuid}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    ##########################################################################
    # public methods
    ##########################################################################

    def lookup(self, pool):
        handle = None
        if isinstance(pool, (tuple, list)):
            handle = list()
            for onepool in pool:
                handle.append(self.lookup(onepool))
            handle = tuple(handle)
        elif isinstance(pool, basestring):
            handle = self._lookupByName(pool)
            if not handle and UUID.validate(pool):
                handle = self._lookupByUUID(pool)
            if not handle:
                log.warn("Unable to find pool {0} on {1}", pool, self._uri)
        return handle

    def list(self, filter=ACTIVE|INACTIVE):
        """list storage pools on this domain

        :param filter: either StoragePoolManager.ACTIVE or StoragePoolManager.INACTIVE 
                       to respectively active or inactive storage pools
        :returns: a tuple containing storage pools names (w.r.t specified filter)
        """
        labels = list()

        filter = filter & (StoragePoolManager.ACTIVE|StoragePoolManager.INACTIVE)
        if not filter or filter & StoragePoolManager.ACTIVE:
            labels.extend(self._list_active())
        if not filter or filter & StoragePoolManager.INACTIVE:
            labels.extend(self._list_inactive())

        return tuple(labels)

    state_desc = {
        POOL_INACTIVE : "is not running",
        POOL_BUILDING : "is initializing pool, not available",
        POOL_RUNNING  : "is running normally",
        POOL_DEGRADED : "is running degraded", 
        POOL_INACCESSIBLE : "is running, but not accessible"
    }

    def state(self, pools):
        """get state of the storage pools specified via pools

        :param pools: either a label, uuid, virStoragePool object or a list
                      of label, uuid, id, a virStoragePool object.
        :returns: (state, a string description) tuple if pools is a label, a
                uuid, a virStoragePool or a tuple of (state, a string
                description) if pool is a list. If an error (state, a
                string description) equals to (None, None).
        """
        result = (None, None)
        if isinstance(pools, libvirt.virStoragePool):
            try:
                state, capacity, allocation, available = pools.info()
                descr = StoragePoolManager.state_desc[state]
                result = (state, descr)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        elif isinstance(pools, basestring):
            result = self.state(self.lookup(pools))
        elif isinstance(pools, (list, tuple)):
            result = list()
            for pool in pools:
                result.append(self.state(pool))
            result = tuple(result)
        return result

    def start(self, pools, flags=0):
        """start specified pools

        :param pools: either a label, uuid, a virStoragePool, a dict (to specify flags) 
                      or a list of label, uuid, virStoragePool object or a list of dict.
        :returns: False if failed, True if success if domains is a label, a uuid,
                a id, a virStoragePool or a tuple if domains is a list. When domain
                is None, returns None.
        """
        result = None
        if isinstance(pools, libvirt.virStoragePool):
            try:
                if pools and not pools.isActive():
                    # extra flags; not used yet, so callers should always pass 0
                    pools.create(flags=0)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(pools, dict):
            if pools.has_key('pool'):
                pool = pools.get('pool', None)
                flags = pools.get('flags', 0)
                result = self.start(pool, flags=0)
        elif isinstance(pools, basestring):
            result = self.start(self.lookup(pools), flags=0)
        elif isinstance(pools, (list, tuple)):
            result = list()
            for pool in pools:
                result.append(self.start(pool, flags=0))
            result = tuple(result)
        return result

    def stop(self, pools):
        """stop specified storage pools

        :param pools: either a label, uuid, a virStoragePool, a dict ('pool'
                      key is used to pass parameter) or a list of label, uuid,
                      virStoragePool object or a list of dict.
        :returns: False if failed, True if success if pools is a label, a uuid,
                  a id, a virStoragePool or a tuple if pools is a list. When pool
                  is None, returns None.
        """
        result = None
        if isinstance(pools, libvirt.virStoragePool):
            try:
                if pools and pools.isActive():
                    pools.destroy()
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(pools, dict):
            if pools.has_key('pool'):
                pool = pools.get('pool', None)
                result = self.stop(pool)
        elif isinstance(pools, basestring):
            result = self.stop(self.lookup(pools))
        elif isinstance(pools, (list, tuple)):
            result = list()
            for pool in pools:
                result.append(self.stop(pool))
            result = tuple(result)
        return result

    def autostart(self, pools, autostart=True):
        """set autostart on specified storage pools

        :param pools: either a label, uuid, a virStoragePool, a dict (to specify flags) 
                      or a list of label, uuid, virStoragePool object or a list of dict.
        :param autostart: default autostart value if not specified otherwise
        :returns: False if failed, True if success if pools is a label, a uuid,
                  a id, a virStoragePool or a tuple if poolss is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(pools, libvirt.virStoragePool):
            try:
                if pools and pools.autostart() != autostart:
                    pools.setAutostart(autostart)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(pools, dict):
            if pools.has_key('pool'):
                pool = pools.get('pool', None)
                autostart = pools.get('autostart', autostart)
                result = self.autostart(pool, autostart)
        elif isinstance(pools, basestring):
            result = self.autostart(self.lookup(pools), autostart)
        elif isinstance(pools, (list, tuple)):
            result = list()
            for pool in pools:
                result.append(self.autostart(pool, autostart))
            result = tuple(result)
        return result
