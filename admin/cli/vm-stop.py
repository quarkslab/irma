import sys, os.path

from lib.irma.machine.libvirt_kvm import KVM

def usage():
    usage = """usage: %s [domain-uri] vm-name

    domain-uri  if not defined, default is 'qemu:///system'
    vm-name     name of the virtual machine
    """
    print(usage % os.path.basename(sys.argv[0]))
    sys.exit(1)

if __name__ == '__main__':

    # always force shutdown
    force = True

    # parameter checking
    if len(sys.argv) not in [2, 3]:
        usage()

    domain_uri = 'qemu:///system'
    if len(sys.argv) == 2:
        vm_name = sys.argv[1]
    else:
        domain_uri = sys.argv[1]
        vm_name = sys.argv[2]

    # performing ops
    try:
        # starting
        virtman = KVM(domain_uri)
        virtman.stop(vm_name, force)
    except:
        sys.exit(1)
