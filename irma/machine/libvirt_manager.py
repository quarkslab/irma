#
# Copyright (c) 2013-2014 QuarksLab.
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
import time
import os.path

from virt.core.domain import DomainManager
from virt.core.storage_pool import StoragePoolManager
from virt.core.storage_volume import StorageVolumeManager
from virt.core.connection import ConnectionManager
from virt.core.exceptions import DomainManagerError

from common.utils import UUID, MAC
from common.oopatterns import ParametricSingleton
from irma.common.exceptions import IrmaMachineManagerError
from .manager import VirtualMachineManager

log = logging.getLogger(__name__)


class LibVirtMachineManager(VirtualMachineManager, ParametricSingleton):
    """Machine manager based on libvirt"""

    # ============================
    #  parametric singleton stuff
    # ============================

    @staticmethod
    def depends_on(cls, *args, **kwargs):
        # singleton is based on the uri, extracted from the libvirt handler
        (handler,) = args[0]
        if isinstance(handler, basestring):
            handler = ConnectionManager(handler)
        if isinstance(handler, ConnectionManager):
            handler = handler.connection
        if not isinstance(handler, libvirt.virConnect):
            what = type(handler)
            reason = "Invalid type for 'connection' field: {0}".format(what)
            raise DomainManagerError(reason)

        try:
            uri = handler.getURI()
        except libvirt.libvirtError as e:
            reason = "unable to get domain uri from connection handle"
            raise DomainManagerError(reason)
        return uri

    # ===================================
    #  Constructor and destructor stuffs
    # ===================================

    def __init__(self, connection):

        self._wait_timeout = 30
        self._connection = ConnectionManager(connection)
        self._domain = DomainManager(connection)

        super(LibVirtMachineManager, self).__init__()

    # =======================
    #  context manager stuff
    # =======================

    def __enter__(self):
        return self

    # =================
    #  Private methods
    # =================

    def _wait(self, label, state, timeout=0):
        """ wait for a vm status to be set.

        :param label: virtual machine name.
        :param state: virtual machine status, accepts many states with a list.
        :raise IrmaMachineManagerError:
            if timeout expire or virtual machine
        """
        if isinstance(state, int):
            state = [state]

        seconds = 0
        current, desc = self._domain.state(label)
        while current not in state:
            if timeout and seconds > int(timeout):
                reason = "status change timeout for '{0}'".format(label)
                raise IrmaMachineManagerError(reason)
            time.sleep(1)
            seconds += 1
            current, desc = self._domain.state(label)

    # ================
    #  public methods
    # ================

    ACTIVE = VirtualMachineManager.ACTIVE
    INACTIVE = VirtualMachineManager.INACTIVE

    def list(self, filter=ACTIVE | INACTIVE):
        """ List all (running and inactive) virtual machines

        :return:
            list of virtual machines names
        :raise IrmaMachineManagerError:
            if unable to list machines
        """
        labels = list()
        try:
            labels.extend(self._domain.list(filter))
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)
        return labels

    def start(self, label):
        """ Start a machine

        :param label: virtual machine name
        :raise IrmaMachineManagerError:
            if unable to start virtual machine.
        """
        state, desc = self._domain.state(label)
        if state != DomainManager.SHUTOFF:
            reason = "{0} should be off, currently {0} {1}".format(label, desc)
            raise IrmaMachineManagerError(reason)
        try:
            res = self._domain.start(label)
            self._wait(label, DomainManager.RUNNING, self._wait_timeout)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def stop(self, label, force=False):
        """ Stop a virtual machine
        :param label: machine name
        :param force: if True, halt machine immediatly instead of gracefully
        :raise IrmaMachineManagerError:
            if unable to stop virtual machine or find it.
        """
        state, desc = self._domain.state(label)
        if state != DomainManager.RUNNING:
            reason = "{0} should be running, {1} instead".format(label, desc)
            raise IrmaMachineManagerError(reason)
        try:
            self._domain.stop(label, force)
            self._wait(label, DomainManager.SHUTOFF, self._wait_timeout)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def clone(self, origin, clone, use_backing_file=True):
        """ Clone a machine
        :param src_label: source machine name
        :param dst_label: destination machine name
        :raise IrmaMachineManagerError:
             if the machine exists or is currently running
        """
        # TODO: move checking in the lib.virt.core api
        state, desc = self._domain.state(origin)
        if state != DomainManager.SHUTOFF:
            reason = "{0} should be off, {1} instead".format(origin, desc)
            raise IrmaMachineManagerError(reason)
        if self._domain.lookup(clone):
            reason = "clone {0} already exists".format(clone, desc)
            raise IrmaMachineManagerError(reason)
        try:
            orig_dict = self._domain.info(origin)
            # if we do not want to use backing files, simply clone
            if not use_backing_file:
                self._domain.clone(origin, clone)
            # we want backing files, check for disks
            else:
                clone_dict = orig_dict
                # generate a new uuid
                while True:
                    uuid = UUID.generate()
                    if not self._domain.lookup(uuid):
                        break
                # set new name and new uuid
                clone_dict['name'] = clone
                clone_dict['uuid'] = uuid
                # change devices
                for type, device in clone_dict['devices'].items():
                    if type == 'interface':
                        interfaces = device
                        if not isinstance(interfaces, list):
                            interfaces = [interfaces]
                        for interface in interfaces:
                            interface['mac']['@address'] = MAC.generate()
                    elif type == 'disk':
                        disks = device
                        if not isinstance(disks, list):
                            disks = [disks]
                        for disk in disks:
                            disk_path = disk['source']['@file']
                            vman = StorageVolumeManager(self._connection, None)
                            pman = StoragePoolManager(self._connection)
                            volume = vman.lookup(disk_path)
                            vman.pool = pman.lookupByVolume(volume)
                            # TODO: pool is not defined, have to create one
                            volume = vman.info(disk_path)
                            # check if has a backing storage
                            if volume.backingstore is not None:
                                from_disk = orig_dict['name']
                                disk_ext = volume.target['format']['@type']
                                to_disk = '.'.join([clone, disk_ext])
                                new_vol = vman.clone(from_disk, to_disk)
                                disk['source']['@file'] = new_vol.path()
                            # create a backing storage
                            else:
                                backingvol = volume
                                backingvol.key = None
                                # retreive path
                                basedir = backingvol.target['path']
                                basedir = os.path.dirname(basedir)
                                disk_ext = volume.target['format']['@type']
                                disk_name = '.'.join([clone, disk_ext])
                                backingvol.target['path'] = \
                                    os.path.join(basedir, disk_name)
                                backingvol.backingstore = \
                                    {'path': disk_path, 'format':
                                        {'@type': disk_ext}}
                                backingvol.name = '.'.join([clone, disk_ext])
                                new_vol = vman.create(backingvol)
                                disk['source']['@file'] = new_vol.path()
                self._domain.create(clone_dict)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def delete(self, label):
        """Delete a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        state, desc = self._domain.state(label)
        if state != DomainManager.SHUTOFF:
            reason = "{0} should be off, {1} instead".format(label, desc)
            raise IrmaMachineManagerError(reason)
        try:
            # TODO: add the possibility to keep some disk
            self._domain.delete(label)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def import_config(self, ordered_dict):
        try:
            self._domain.create(ordered_dict)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def export_config(self, label):
        try:
            return self._domain.info(label)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)
