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

from ...virt.core.domain import DomainManager

log = logging.getLogger(__name__)


class MachineManager(object):
    """abstract class for machine manager"""

    UNDEFINED = 0
    RUNNING = 1
    HALTED = 2
    SUSPENDED = 3


class VirtualMachineManager(MachineManager):
    """abstract class for a virtual machine manager"""

    # ===========
    #  constants
    # ===========

    # Available state
    ACTIVE = DomainManager.ACTIVE
    INACTIVE = DomainManager.INACTIVE

    # ==================
    #  public interface
    # ==================

    def list(self, filter=ACTIVE | INACTIVE):
        """List machines.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def start(self, label):
        """Start a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def stop(self, label, force=False):
        """Stop a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def clone(self, src_label, dst_label):
        """Clone a machine
        @param src_label: source machine name
        @param dst_label: destination machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def delete(self, label):
        """Delete a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError
