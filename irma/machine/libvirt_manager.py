import time, logging, random, os.path

from lxml import etree

from lib.irma.common.exceptions import IrmaMachineManagerError
from lib.irma.machine.manager import VirtualMachineManager

log = logging.getLogger(__name__)

# TODO: move this function to a separate python file
def _status_str(state):
    """Converts a int representing a state to a string"""
    default = 0
    state_str = ("Undefined", "Running", "Halted", "Supended")
    try:
        status = state_str[state]
    except IndexError:
        log.error("State %d cannot be converted to string, setting to '' by default", state, state_str[default])
        status = state_str[default]
    return status

# TODO: move this function to a separate python file
def _random_uuid():
    return [ random.randint(0, 255) for dummy in range(0, 16) ]

# TODO: move this function to a separate python file
def _uuid_to_str(u):
    return "-".join(["%02x" * 4, "%02x" * 2, "%02x" * 2, "%02x" * 2, "%02x" * 6]) % tuple(u)

# TODO: improve mac generation
# TODO: move this function to a separate python file
def _random_mac(oui=None):
    if not oui or len(oui) != 3:
        oui = [ 0x52, 0x54, 0x00 ]
    mac = oui + [
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))

class LibVirtMachineManager(VirtualMachineManager):
    """Machine manager based on libvirt"""

    ##########################################################################
    # Constructor and destructor stuffs
    ##########################################################################

    def __init__(self, driver=None, prefetch=True):
        try:
            global libvirt
            import libvirt
        except ImportError:
            raise IrmaDependencyError("Unable to import libvirt")

        # TODO: move these parameters in a configuration file
        self._prefetch = None
        self._wait_timeout = 30
        self._auto_restore_snapshot = False

        self._conn = None
        self._vms = dict()
        self._driver = driver
        if prefetch is not None:
            self._prefetch = prefetch

        self._connect()
        if self._prefetch:
            self._prefetch_machines()

        super(LibVirtMachineManager, self).__init__()

    def __del__(self):
        if self._conn:
            self._disconnect()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self._conn:
            self._disconnect()

    ##########################################################################
    # Parametric Singleton
    ##########################################################################
    # TODO: create a metaclass

    _instances = dict()

    def __new__(cls, *args, **kwargs):
        key = None
        if len(args) > 0:
            key = args[0]
        if "driver" in kwargs:
            key = kwargs["driver"]
        if key not in LibVirtMachineManager._instances:
            LibVirtMachineManager._instances[key] = super(LibVirtMachineManager, cls).__new__(cls, *args, **kwargs)
        return LibVirtMachineManager._instances[key]

    ##########################################################################
    # Private methods
    ##########################################################################

    def _connect(self):
        """Connect to libvirt subsystem.
        @raise IrmaMachineManagerError: if cannot connect to libvirt or missing connection string.
        """
        if not self._conn:
            try:
                self._conn = libvirt.open(self._driver)
            except libvirt.libvirtError as e:
                raise IrmaMachineManagerError("{0}".format(e))
        else:
            log.warn("Trying to connect while an libvirt instance exists")

    def _disconnect(self):
        """Disconnect from a libvirt subsystem.
        @raise IrmaMachineManagerError: if cannot disconnect from libvirt.
        """
        # check if connection has been initialized
        if self._conn: 
            try:
                self._conn.close()
                self._conn = None
            except libvirt.libvirtError:
                raise IrmaMachineManagerError("{0}".format(e))
        else:
            log.warn("Trying to disconnect from an inexistant libvirt instance")

    def _inactive_machines(self):
        labels = list()
        try:
            labels = self._conn.listDefinedDomains()
            log.debug("Inactive machines for '%s': '%s'", self._driver, ' '.join(labels))
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("{0}".format(e))
        return labels
    
    def _active_machines(self):
        labels = list()
        try:
            ids = self._conn.listDomainsID()
            for id in ids:
                labels.append(self._conn.lookupByID(id).name())
            log.debug("Active machines for '%s': '%s'", self._driver, ' '.join(labels))
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("{0}".format(e))
        return labels

    def _prefetch_machines(self):
        """Fill the cache with all known virtual machines
        @return libvirt objects to manipulate virtual machines
        @raise IrmaMachineManagerError: if unable to list machines
        """
        labels = self.all_machines()
        try:
            for label in labels:
                self._lookup(label)
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("{0}".format(e))
        return self._vms

    def _lookup(self, label):
        """Look for a virtual machine by his name
        @param label: machine name
        @return libvirt object for the virtual machine
        @raise IrmaMachineManagerError: if unable to find machine
        """
        # object instance is in cache
        if label in self._vms:
            machine = self._vms[label]
            log.debug("Fetching libvirt object instance for '%s' from cache.", label)
        # object instance is not in cache, add it to cache.
        else:
            try:
                machine = self._conn.lookupByName(label)
                self._vms[label] = machine
            except libvirt.libvirtError as e:
                raise IrmaMachineManagerError("{0}".format(e))
            log.debug("Added libvirt object instance for '%s' in cache.", label)
        return machine

    def _status(self, label):
        """Get the status of the virtual machine
        @param label: virtual machine name.
        @return status of the virtual machine
        @raise IrmaMachineManagerError if unable to get status or unable to find machine
        """
        try:
            machine = self._lookup(label)
            # flags not used yet, so callers should always pass 0
            state, reason = machine.state(flags=0)
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("{0}".format(e))
        # converting the libvirt state to an internal status
        if state == libvirt.VIR_DOMAIN_RUNNING:
            status = self.RUNNING
        elif state == libvirt.VIR_DOMAIN_PAUSED or \
             state == libvirt.VIR_DOMAIN_PMSUSPENDED:
            status = self.SUSPENDED
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            status = self.HALTED
        else:
            status = self.UNDEFINED
        log.debug("'%s' has status %d with reason %d (state %d '%s')",
                  label, state, reason, status, _status_str(status))
        return status

    def _wait(self, label, state):
        """Waits for a vm status.
        @param label: virtual machine name.
        @param state: virtual machine status, accepts more than one states in a list.
        @raise IrmaMachineManagerError: if default waiting timeout expire or unable to find machine
        """
        current = self._status(label)
        if isinstance(state, int):
            state = [state]

        seconds = 0
        while current not in state:
            if seconds > int(self._wait_timeout):
                raise IrmaMachineManagerError("Timeout hit for machine {0} to change status".format(label))
            time.sleep(1)
            seconds += 1
            current = self._status(label)
            print(current, state)

    def _uuid_collision(self, uuid):
        collision = False
        if uuid is not None:
            try:
                if self._conn.lookupByUUIDString(uuid):
                    return True
            except:
                pass
        return collision

    def _clone_disk(self, src_disk, dst_disk):
        if not src_disk or not dst_disk:
            raise IrmaMachineManagerError("Invalid parameters")
        try:
            volume = self._conn.storageVolLookupByPath(src_disk)
            disk_path = os.path.basename(src_disk)
            # Modify xml
            src_xml = volume.XMLDesc(0)
            log.debug("Initial XML file for disk '%s'", src_disk)
            log.debug("%s", src_xml)
            dst_xml = etree.fromstring(src_xml)
            # Change name
            dst_xml.xpath("/volume/name")[0].text = dst_disk
            # Change key
            dst_xml.xpath("/volume/key")[0].text = "{0}/{1}".format(disk_path, dst_disk)
            dst_xml.xpath("/volume/target/path")[0].text = "{0}/{1}".format(disk_path, dst_disk)
            # Create new disk
            dst_xml = etree.tostring(dst_xml)
            log.debug("Modified XML file for disk '%s'", dst_disk)
            log.debug("%s", dst_xml)
            pool = volume.storagePoolLookupByVolume()
            pool.createXML(dst_xml, 0)
        except Exception as e:
            raise IrmaMachineManagerError("Couldn't lookup volume object: {0}".format(e))

    def _clone_machine(self, src_label, dst_label):
        if not src_label or not dst_label:
            raise IrmaMachineManagerError("Invalid parameters")

        try:
            machine = self._lookup(src_label)
            # dumping configuration for next boot
            src_xml = machine.XMLDesc(libvirt.VIR_DOMAIN_XML_INACTIVE)
            log.debug("Initial XML configuration (from '%s')", src_label)
            log.debug("%s", src_xml)
            try:
                dst_xml = etree.fromstring(src_xml)
                # modify machine name
                name_tag = dst_xml.xpath("name")
                name_tag[0].text = dst_label
                # modify uuid
                while True:
                    uuid = _uuid_to_str(_random_uuid())
                    # Check for uuid collisions
                    if not self._uuid_collision(uuid):
                        break
                uuid_tag = dst_xml.xpath("uuid")
                uuid_tag[0].text = uuid
                # modify mac
                macs_tag = dst_xml.xpath("devices/interface/mac[@address]")
                for mac in macs_tag:
                    mac.attrib["address"] = _random_mac()
                # modify disk
                disk_source_tag = dst_xml.xpath("devices/disk[contains(@device, 'disk')]/source")
                src_disk = disk_source_tag[0].attrib["file"]
                extension = os.path.splitext(src_disk)[1]
                directory = os.path.dirname(src_disk)
                dst_disk = "{0}{1}".format(uuid, extension)
                disk_source_tag[0].attrib["file"] = "{0}/{1}".format(directory, dst_disk)
                # clone disk
                self._clone_disk(src_disk, dst_disk)
                # create a new virtual machine
                dst_xml = etree.tostring(dst_xml)
                log.debug("XML configuration for '%s'", dst_label)
                log.debug("%s", dst_xml)
                self._conn.defineXML(dst_xml)
            except Exception as e:
                 raise IrmaMachineManagerError("Error cloning virtual machine {0} to {1}: {2}".format(src_label, dst_label, e))
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("Error cloning virtual machine {0} to {1}: {2}".format(src_label, dst_label, e))
   

    ##########################################################################
    # public methods
    ##########################################################################

    def all_machines(self):
        """List all (running and inactive) virtual machines 
        @return list of virtual machines names
        @raise IrmaMachineManagerError: if unable to list machines
        """
        labels = list()
        labels.extend(self.running_machines())
        labels.extend(self.inactive_machines())
        return labels

    def running_machines(self):
        """List all running virtual machines 
        @return list of virtual machines names
        @raise IrmaMachineManagerError: if unable to list machines
        """
        return self._active_machines()

    def inactive_machines(self):
        """List all virtual machines 
        @return list of virtual machines names
        @raise IrmaMachineManagerError: if unable to list machines
        """
        return self._inactive_machines()

    def start(self, label):
        """Start a machine
        @param label: virtual machine name
        @raise IrmaMachineManagerError: if unable to start virtual machine.
        """
        log.debug("Starting machine '%s'", label)
        
        # sanity checks
        if self._status(label) == self.UNDEFINED:
            raise IrmaMachineManagerError("'{0}' is in an unhandled state, please check for logs".format(label))
        elif self._status(label) == self.RUNNING:
            raise IrmaMachineManagerError("'{0}' is already started".format(label))
        # check for a snapshot and revert to it, then launch
        try:
            machine = self._lookup(label)
            if self._auto_restore_snapshot:
                # flags not used yet, so callers should always pass 0
                snap = machine.hasCurrentSnapshot(flags=0)
                if snap:
                    current = machine.snapshotCurrent(flags=0)
                    machine.revertToSnapshot(current, flags=0)
                else:
                    log.warn("Beware ! '%s' does not have a snapshot.", label)
                    machine.create()
            else:
                machine.create()
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("{0}".format(e))
        # wait for status to change.
        self._wait(label, self.RUNNING)

    def stop(self, label, force=False):
        """Stop a virtual machine
        @param label: machine name
        @param force: if True, halt machine immediatly instead of gracefully
        @raise IrmaMachineManagerError: if unable to stop virtual machine or find it.
        """
        if self._status(label) == self.HALTED:
            raise IrmaMachineManagerError("Trying to stop an already stopped machine {0}".format(label))
        try:
            machine = self._lookup(label)
            if not machine.isActive():
                log.debug("Trying to stop an already stopped machine %s. Skip", label)
            else:
                if not force:
                    machine.shutdown() 
                else:
                    machine.destroy()
                    log.debug("Forcing shutdown for '%s'", label)
        except libvirt.libvirtError as e:
            raise IrmaMachineManagerError("Error stopping virtual machine {0}: {1}".format(label, e))
        self._wait(label, self.HALTED)

    def clone(self, src_label=None, dst_label=None):
        """Clone a machine
        @param src_label: source machine name
        @param dst_label: destination machine name
        @raise NotImplementedError: this method is abstract.
        """
        if self._status(src_label) == self.RUNNING:
            raise IrmaMachineManagerError("Cannot clone a running machine {0}".format(src_label))
        self._clone_machine(src_label, dst_label)

    def remove(self, label=None):
        """Delete a machine
        @param label: machine name
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError
