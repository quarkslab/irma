import logging, unittest, os

from lib.irma.common.exceptions import IrmaMachineManagerError
from lib.irma.machine.libvirt_manager import LibVirtMachineManager
from lib.irma.machine.libvirt_kvm import KVM


##############################################################################
# Logging options
##############################################################################
def enable_logging(level=logging.INFO, handler=None, formatter=None):
    global log
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)

KVM_URI="qemu+tcp://IrmaSonde.usr.qb/system"

if __name__ == '__main__':
    enable_logging(logging.DEBUG)

    # Listing machines
    log.debug("[*] Connecting to '{0}'".format(KVM_URI))
    mmanager = KVM(KVM_URI)
    log.info("available machines: {0}".format(mmanager.all_machines()))
    log.info("running machines: {0}".format(mmanager.running_machines()))
    log.info("stopped machines: {0}".format(mmanager.inactive_machines()))
    
    # Cloning machines
    clone_vm_name = "winxp-qemu-clone"
    vm_name = "winxp-qemu"
    log.debug("[*] Cloning machine '{0}' to '{1}' on '{2}'".format(vm_name, clone_vm_name, KVM_URI))
    #mmanager.clone(vm_name, clone_vm_name)

    # Deleting machine
    mmanager.delete(clone_vm_name)
