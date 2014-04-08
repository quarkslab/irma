from lib.irma.machine.libvirt_manager import LibVirtMachineManager


class KVM(LibVirtMachineManager):
    """KVM machine manager based on python-libvirt"""

    def __init__(self, driver=None):
        if not driver:
            driver = "qemu:///system"
        super(KVM, self).__init__(driver)

    def __new__(cls, *args, **kwargs):
        # if no driver defined, set 'qemu:///system'
        if not len(args) and not "driver" in kwargs:
            kwargs["driver"] = "qemu:///system"
        return super(KVM, cls).__new__(cls, *args, **kwargs)
