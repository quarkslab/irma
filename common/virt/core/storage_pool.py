#
# Copyright (c) 2013-2016 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import logging
import libvirt

from common.utils import UUID
from common.oopatterns import ParametricSingleton
from .connection import ConnectionManager
from .exceptions import StoragePoolManagerError

log = logging.getLogger(__name__)


class StoragePoolManager(ParametricSingleton):
    """
    Storage pool manager to a manage storage on
    local or remote virtual machine manager
    """

    # ============================
    #  parametric singleton stuff
    # ============================

    @staticmethod
    def depends_on(cls, *args, **kwargs):
        # singleton is based on the uri, extracted from the libvirt handler
        (handler,) = args[0]
        if isinstance(handler, str):
            handler = ConnectionManager(handler)
        if isinstance(handler, ConnectionManager):
            handler = handler.connection
        try:
            uri = handler.getURI()
        except libvirt.libvirtError as e:
            log.exception(e)
            raise StoragePoolManagerError(e)
        return uri

    # ===========
    #  Constants
    # ===========

    # =================
    #  Available state
    # =================

    ACTIVE = 1
    INACTIVE = 2

    # ==================
    #  Available status
    # ==================

    POOL_INACTIVE = libvirt.VIR_STORAGE_POOL_INACTIVE
    POOL_BUILDING = libvirt.VIR_STORAGE_POOL_BUILDING
    POOL_RUNNING = libvirt.VIR_STORAGE_POOL_RUNNING
    POOL_DEGRADED = libvirt.VIR_STORAGE_POOL_DEGRADED
    POOL_INACCESSIBLE = libvirt.VIR_STORAGE_POOL_INACCESSIBLE

    # ========================
    #  Available delete flags
    # ========================

    # Delete metadata only (fast)
    DELETE_NORMAL = libvirt.VIR_STORAGE_POOL_DELETE_NORMAL
    # Clear all data to zeros (slow)
    DELETE_ZEROED = libvirt.VIR_STORAGE_POOL_DELETE_ZEROED

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, connection, prefetch=False):
        """Instantiate a storage pool manager for specified connection

        :param connection: either an instance of a ``ConnectionManager``
            or directly a libvirt connection handler
        :param prefetch: set to True if prefetching storage pool handlers
            for this connection is required
        :raises: StoragePoolManagerError if ``connection`` is not an
            expected type or None
        """
        # handle cache
        self._cache = {'name': {}, 'uuid': {}}
        # get libvirt.virConnection from connection
        self._set_drv(connection)
        # prefetch list of handlers
        if prefetch:
            list(map(lambda name: self._lookup(_lookupByName(name)),
                     self.list()))

    # =======================
    #  context manager stuff
    # =======================

    def __enter__(self):
        return self

    # ==================
    #  internal helpers
    # ==================

    # libvirt.virConnection from connection
    def _set_drv(self, connection):
        self._drv = connection
        if isinstance(self._drv, str):
            self._drv = ConnectionManager(self._drv)
        if isinstance(self._drv, ConnectionManager):
            self._drv = self._drv.connection

    def _list_active(self):
        labels = list()
        try:
            labels.extend(self._drv.listStoragePools())
        except libvirt.libvirtError as e:
            raise StoragePoolManagerError(e)
        return tuple(labels)

    def _list_inactive(self):
        labels = list()
        try:
            labels.extend(self._drv.listDefinedStoragePools())
        except libvirt.libvirtError as e:
            raise StoragePoolManagerError(e)
        return tuple(labels)

    def _cache_handle(self, cache, entry, where=None):
        if not isinstance(cache, dict):
            raise ValueError("'cache' fields must be a dict")
        if where and entry:
            for key, value in list(where.items()):
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
                handle = self._drv.storagePoolLookupByName(name)
                uuid = handle.UUIDString()
                where = {'name': name, 'uuid': uuid}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                # do not raise an exception here, we put a simple warning
                log.warn(e)
        return handle

    def _lookupByUUID(self, uuid):
        handle = None
        # check if storage pool has already been cached
        if uuid in self._cache['uuid']:
            handle = self._cache['uuid'][uuid]
        # storage pool not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.storagePoolLookupByUUIDString(uuid)
                name = handle.name()
                where = {'name': name, 'uuid': uuid}
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                # do not raise an exception here, we put a simple warning
                log.warn(e)
        return handle

    def _lookup_pool(self, name):
        pool = self.lookup(name)
        if not pool:
            raise StoragePoolManagerError("Pool '{0}' not found".format(name))
        return pool

    # ================
    #  public methods
    # ================

    def lookup(self, pool):
        handle = None
        if isinstance(pool, str):
            handle = self._lookupByName(pool)
            if not handle and UUID.validate(pool):
                handle = self._lookupByUUID(pool)
        # TODO: in the future, handle storage pool objects
        # warn if no handle has been found
        if not handle:
            log.warn("Unable to find pool '{0}'".format(pool) +
                     " on '{1}'".format(self._drv.getURI()))
        # return handle
        return handle

    def list(self, filter=ACTIVE | INACTIVE):
        """list storage pools on this domain

        :param filter: either StoragePoolManager.ACTIVE or
            StoragePoolManager.INACTIVE
            to respectively active or inactive storage pools
        :returns: a tuple containing storage pools names
            (w.r.t specified filter)
        """
        labels = list()
        # modifying filters
        mask = (StoragePoolManager.ACTIVE |
                StoragePoolManager.INACTIVE)
        filter = filter & mask
        # fetching labels according to filters
        if not filter or filter & StoragePoolManager.ACTIVE:
            labels.extend(self._list_active())
        if not filter or filter & StoragePoolManager.INACTIVE:
            labels.extend(self._list_inactive())
        return tuple(labels)

    state_desc = {
        POOL_INACTIVE:     "is not running",
        POOL_BUILDING:     "is initializing pool, not available",
        POOL_RUNNING:      "is running normally",
        POOL_DEGRADED:     "is running degraded",
        POOL_INACCESSIBLE: "is running, but not accessible"
    }

    def state(self, pool):
        """get state of the storage pool specified via pool

        :param pool: either a label, uuid, virStoragePool object
        :returns: (state, a string description) tuple if pool is
            a label, a uuid, a virStoragePool.
        """
        result = (None, None)
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirt.virStoragePool):
            try:
                state, capacity, allocation, available = pool.info()
                descr = StoragePoolManager.state_desc[state]
                result = (state, descr)
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)
        return result

    def start(self, pool, flags=0):
        """start specified pool

        :param pool: either a label, uuid, a virStoragePool
        """
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        if isinstance(pool, libvirt.virStoragePool):
            try:
                if not pool.isActive():
                    e = "Pool '{0}' is not active, aborting.".format(pool)
                    log.error(e)
                    raise StoragePoolManagerError(e)
                # extra flags; not used yet, so callers should always pass 0
                flags = flags & 0
                pool.create(flags=flags)
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)

    def stop(self, pool):
        """stop specified storage pool

        :param pool: either a label, uuid, a virStoragePool
        """
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirt.virStoragePool):
            try:
                if not pool.isActive():
                    e = "Pool '{0}' is not active, aborting.".format(pool)
                    log.error(e)
                    raise StoragePoolManagerError(e)
                pool.destroy()
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)

    def delete(self, pool, flags=0):
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirt.virStoragePool):
            try:
                # sanitize flags
                mask = StoragePoolManager.DELETE_NORMAL
                mask |= StoragePoolManager.DELETE_ZEROED
                flags = flags & mask
                pool.delete(flags=flags)
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)

    def autostart(self, pool, autostart=None):
        """set autostart on specified storage pools

        :param pools: either a label, uuid, a virStoragePool
        """
        result = None
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirt.virStoragePool):
            try:
                result = pool.autostart()
                if autostart is not None:
                    if result != autostart:
                        pool.setAutostart(autostart)
                        result = autostart
                    else:
                        log.warn("Pool {0} already have".format(pool) +
                                 " autostart set to '{0}'".format(result))
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)
        return result

    def active(self, pool):
        result = None
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirtError.virStoragePool):
            try:
                result = pool.isActive()
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)
        return result

    def persistent(self, pool):
        result = None
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirtError.virStoragePool):
            try:
                result = pool.isPersistent()
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)
        return result

    def refresh(self, pool, flags=0):
        if isinstance(pool, str):
            pool = self._lookup_pool(pool)
        # TODO: in the future, handle storage pool objects
        if isinstance(pool, libvirtError.virStoragePool):
            try:
                # extra flags; not used yet, so callers should always pass 0
                flags = flags & 0
                pool.refresh(flags=flags)
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)

    def lookupByVolume(self, volume):
        from virt.core.storage_volume import StorageVolumeManager
        pool = None
        if isinstance(volume, str):
            volman = StorageVolumeManager(self._drv, None)
            volume = volman.lookup(volume)
        if isinstance(volume, libvirt.virStorageVol):
            try:
                pool = volume.storagePoolLookupByVolume()
                # update pool in volume manager instance
                volman = StorageVolumeManager(self._drv, None)
                volman.pool = pool
            except libvirt.libvirtError as e:
                log.exception(e)
                raise StoragePoolManagerError(e)
        return pool
