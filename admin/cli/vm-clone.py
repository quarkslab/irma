import sys, os.path

from lib.irma.machine.libvirt_kvm import KVM

def usage():
    usage = """usage: %s [domain-uri] vm-name vm-clone

    domain-uri  if not defined, default is 'qemu:///system'
    vm-name     name of the virtual machine to clone
    vm-clone    name of the newly created virtual machine

    """
    print(usage % os.path(sys.argv[0]))
    sys.exit(1)

if __name__ == '__main__':

    # parameter checking
    if len(sys.argv) not in [3, 4]:
        usage()

    domain_uri = 'qemu:///system'
    if len(sys.argv) == 3:
        vmname = sys.argv[1]
        clonename = sys.argv[2]
    elif len(sys.argv) == 4:
        domain_uri = sys.argv[1]
        vmname = sys.argv[2]
        clonename = sys.argv[3]
    
    # performing ops
    try:
        # starting
        print "Cloning %s to %s on domain %s" % (vmname, clonename, domain_uri)
        virtman = KVM(domain_uri)
	virtman.clone(vmname, clonename)
    except:
        sys.exit(1)
