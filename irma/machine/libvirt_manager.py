import logging, libvirt, time, random, os.path

from lib.virt.core.domain import DomainManager
from lib.virt.core.storage_pool import StoragePoolManager
from lib.virt.core.storage_volume import StorageVolumeManager
from lib.virt.core.connection import ConnectionManager
from lib.virt.core.exceptions import DomainManagerError

from lib.irma.common.oopatterns import ParametricSingleton
from lib.irma.common.exceptions import IrmaMachineManagerError
from lib.irma.machine.manager import VirtualMachineManager

log = logging.getLogger(__name__)

class LibVirtMachineManager(VirtualMachineManager, ParametricSingleton):
    """Machine manager based on libvirt"""

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
        if not isinstance(handler, libvirt.virConnect):
            raise DomainManagerError("'connection' field type '{0}' is not valid".format(type(connection)))

        try:
            uri = handler.getURI()          
        except libvirt.libvirtError as e:
            raise DomainManagerError("unable to get domain uri from connection handle")
        return uri

    ##########################################################################
    # Constructor and destructor stuffs
    ##########################################################################

    def __init__(self, connection):

        self._wait_timeout = 30
        self._connection = ConnectionManager(connection)
        self._domain = DomainManager(connection)

        super(LibVirtMachineManager, self).__init__()

    ##########################################################################
    # context manager stuff
    ##########################################################################

    def __enter__(self):
        return self

    ##########################################################################
    # Private methods
    ##########################################################################

    def _wait(self, label, state, timeout=0):
        """Waits for a vm status.
        @param label: virtual machine name.
        @param state: virtual machine status, accepts more than one states in a list.
        @raise IrmaMachineManagerError: if default waiting timeout expire or unable to find machine
        """
        if isinstance(state, int):
            state = [state]

        seconds = 0
        current, desc = self._domain.state(label)
        while current not in state:
            if timeout and seconds > int(timeout):
                raise IrmaMachineManagerError("Timeout hit for machine {0} to change status".format(label))
            time.sleep(1)
            seconds += 1
            current, desc = self._domain.state(label)

    ##########################################################################
    # public methods
    ##########################################################################

    def list(self, filter=VirtualMachineManager.ACTIVE|VirtualMachineManager.INACTIVE):
        """List all (running and inactive) virtual machines 
        @return list of virtual machines names
        @raise IrmaMachineManagerError: if unable to list machines
        """
        labels = list()
        try:
            labels.extend(self._domain.list(filter))
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)
        return labels

    def start(self, label):
        """Start a machine
        @param label: virtual machine name
        @raise IrmaMachineManagerError: if unable to start virtual machine.
        """
        state, desc = self._domain.state(label)
        if state != DomainManager.SHUTOFF:
            raise IrmaMachineManagerError("{0} should be off, currently {0} {1}".format(label, desc))
        try:
            res = self._domain.start(label)
            self._wait(label, DomainManager.RUNNING, self._wait_timeout)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def stop(self, label, force=False):
        """Stop a virtual machine
        @param label: machine name
        @param force: if True, halt machine immediatly instead of gracefully
        @raise IrmaMachineManagerError: if unable to stop virtual machine or find it.
        """
        state, desc = self._domain.state(label)
        if state != DomainManager.RUNNING:
            raise IrmaMachineManagerError("{0} should be running, currently {0} {1}".format(label, desc))
        try:
            self._domain.stop(label, force)
            self._wait(label, DomainManager.SHUTOFF, self._wait_timeout)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def clone(self, origin, clone):
        """Clone a machine
        @param src_label: source machine name
        @param dst_label: destination machine name
        @raise NotImplementedError: this method is abstract.
        """
        state, desc = self._domain.state(origin)
        if state != DomainManager.SHUTOFF:
            raise IrmaMachineManagerError("{0} should be off, currently {0} {1}".format(origin, desc))
        
        if self._domain.lookup(clone):
            raise IrmaMachineManagerError("clone {0} already exists".format(clone, desc))

        try:
            # TODO: check if has a backing storage
            # if not, create a backing storage and use create instead of clone
            self._domain.clone(origin, clone)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)

    def delete(self, label):
        """Delete a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        state, desc = self._domain.state(label)
        if state != DomainManager.SHUTOFF:
            raise IrmaMachineManagerError("{0} should be off, currently {0} {1}".format(origin, desc))
        
        try:
            # TODO: add the possibility to keep some disk
            self._domain.delete(label)
        except DomainManagerError as e:
            raise IrmaMachineManagerError(e)
