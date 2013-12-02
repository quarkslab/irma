import logging

log = logging.getLogger(__name__)

class MachineManager(object):
    """abstract class for machine manager"""

    UNDEFINED = 0
    RUNNING   = 1
    HALTED    = 2
    SUSPENDED = 3

    def __init__(self):
        pass

    def all_machines(self):
        """List machines.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def running_machines(self):
        """List machines.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def inactive_machines(self):
        """List machines.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def acquire(self, label=None):
        """Acquire a machine to start analysis.
        @param label: machine name.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def release(self, label=None):
        """Release a machine.
        @param label: machine name.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError
   
    def shutdown(self):
        """Shutdown the machine manager. Kills all alive machines.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError


class VirtualMachineManager(MachineManager):
    """abstract class for a virtual machine manager"""

    def __init__(self):
        pass

    def start(self, label=None):
        """Start a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def stop(self):
        """Stop a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def clone(self, src_label=None, dst_label=None):
        """Clone a machine
        @param src_label: source machine name
        @param dst_label: destination machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def delete(self, label=None):
        """Delete a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError
