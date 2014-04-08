import logging

from virt.core.domain import DomainManager

log = logging.getLogger(__name__)


class MachineManager(object):
    """abstract class for machine manager"""

    UNDEFINED = 0
    RUNNING = 1
    HALTED = 2
    SUSPENDED = 3


class VirtualMachineManager(MachineManager):
    """abstract class for a virtual machine manager"""

    ##########################################################################
    # constants
    ##########################################################################

    # Available state
    ACTIVE = DomainManager.ACTIVE
    INACTIVE = DomainManager.INACTIVE

    ##########################################################################
    # public interface
    ##########################################################################

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
