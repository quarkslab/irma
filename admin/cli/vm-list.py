import sys, os.path

from lib.irma.machine.libvirt_kvm import KVM

def usage():
    usage = """usage: %s [domain-uri] [filter]

    domain-uri  if not defined, default is 'qemu:///system'
    filter      either 'active-only', 'inactive-only', 'all'

    """
    print(usage % os.path(sys.argv[0]))
    sys.exit(1)

if __name__ == '__main__':

    # parameter checking
    if len(sys.argv) not in [1, 2, 3]:
        usage()

    domain_uri = 'qemu:///system'
    val = 'all'

    if len(sys.argv) == 2:
        domain_uri = sys.argv[1]
    elif len(sys.argv) == 3:
        domain_uri = sys.argv[1]
        val = sys.argv[2]
    
    if val not in ['active-only', 'inactive-only', 'all']:
        print 'Invalid filter, fallback to all'
        filter = 'all'
    else:
        filter = val

    # performing ops
    try:
        # starting
        virtman = KVM(domain_uri)
        if filter == 'all':
            print 'All machines on %s:' % domain_uri
            for name in virtman.all_machines():
                print "    %s" % name
        elif filter == 'active-only':
            print 'Active machines on %s:' % domain_uri
            for name in virtman.running_machines():
                print "    %s" % name
        elif filter == 'inactive-only':
            print 'Inactive machines on %s:' % domain_uri
            for name in virtman.inactive_machines():
                print "    %s" % name
    except:
        sys.exit(1)
