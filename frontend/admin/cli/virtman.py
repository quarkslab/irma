#!/bin/bash

import argparse, sys, string

from lib.virt.core.domain import DomainManager
from lib.virt.core.connection import ConnectionManager
from lib.virt.core.exceptions import ConnectionManagerError, DomainManagerError

##############################################################################
# metas
##############################################################################

__version__ = '0.0.1'
__date__    = '2013-12-19'

##############################################################################
# command-line arguments parser
##############################################################################

parser = argparse.ArgumentParser(description='IRMA - Virtual Machine Manager')

parser.add_argument('-c', '--connect', dest='uri', action='append', default=[], help='connect to the specified URI')
parser.add_argument('-r', '--read-only', dest='readonly', action="store_true", default=False)
parser.add_argument('-d', '--debug', dest='level', action='store', type=int, default=0, help='Enable debug messages at integer LEVEL and above.', choices=[0, 1, 2, 3])
parser.add_argument('-v', '--version', action='version', version=' '.join(['%(prog)s', '(version %s)' % __version__]))

##############################################################################
# subcommands arguments parsers
##############################################################################

domparser = parser.add_subparsers(title='guest management sub-commands', help='available sub-commands to manage virtual machines', dest='subcommand')

# vmlist
vmlist_parser = domparser.add_parser('vmlist', help='shut down an active domain')
vmlist_group = vmlist_parser.add_mutually_exclusive_group()
vmlist_group.add_argument('-a', '--active-only', action='store_true', help='list only active domains')
vmlist_group.add_argument('-i', '--inactive-only', action='store_true', help='list only inactive domains')

# vmstate
vmstate_parser = domparser.add_parser('vmstate', help='show the state of a virtual machine')
vmstate_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to query')

# vmstart
vmstart_parser = domparser.add_parser('vmstart', help='start a (previously defined) inactive domain')
vmstart_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to start')

# vmshutdown
vmshutdown_parser = domparser.add_parser('vmshutdown', help='shut down an active domain')
vmshutdown_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to stop')
vmshutdown_parser.add_argument('-f', '--force', action='store_true', help='shut down the specified domains immediately')
vmshutdown_parser.add_argument('-m', '--mode', dest='mode', action='store', default='', choices=['acpi', 'agent', 'gracefully'], help='shutdown mode: acpi|agent|gracefully')

# vmautostart
vmautostart_parser = domparser.add_parser('vmautostart', help='autostart a domain')
vmautostart_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain')
vmautostart_parser.add_argument('-d', '--disable', action='store_true', help='disable autostart')

# vmreboot
vmreboot_parser = domparser.add_parser('vmreboot', help='reboot a domain')
vmreboot_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to reboot')
vmreboot_parser.add_argument('-m', '--mode', dest='mode', action='store', default='', choices=['acpi', 'agent'], help='shutdown mode: acpi|agent')

# vmreset
vmreset_parser = domparser.add_parser('vmreset', help='reset a domain')
vmreset_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to reset')

# vmresume
vmresume_parser = domparser.add_parser('vmresume', help='resume a previously suspended domain')
vmresume_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to resume')

# vmsuspend
vmsuspend_parser = domparser.add_parser('vmsuspend', help='suspend an active domain')
vmsuspend_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to suspend')

# vmscreenshot
vmscreenshot_parser = domparser.add_parser('vmscreenshot', help='screenshot of a current domain')
vmscreenshot_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain')
vmscreenshot_parser.add_argument('-s', '--screen', type=int, action='store', default=0, help='screen on which perform screenshot')
vmscreenshot_parser.add_argument('-f', '--filename', type=str, default=None, action='store', help='output filename')

# vmcoredump
vmcoredump_parser = domparser.add_parser('vmcoredump', help='perform a coredump on a domain')
vmcoredump_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain')
vmcoredump_parser.add_argument('-f', '--filename', type=str, default=None, action='store', help='output filename')
vmcoredump_parser.add_argument('-m', '--mode', dest='mode', action='store', default='live', choices=['reset', 'crash', 'live', 'bypass-cache'], help='mode: reset|crash|live|bypass-cache')

# vmmemdump
vmmemdump_parser = domparser.add_parser('vmmemdump', help='perform a memdump on a domain')
vmmemdump_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain')
vmmemdump_parser.add_argument('-b', '--base', type=int, default=0, action='store', help='start address')
vmmemdump_parser.add_argument('-s', '--size', type=int, default=64*1024, action='store', help='size in bytes')
vmmemdump_parser.add_argument('-f', '--filename', type=str, default=None, action='store', help='output filename')
vmmemdump_parser.add_argument('-m', '--mode', dest='mode', action='store', default='physical', choices=['physical', 'virtual'], help='mode: virtual|physical')

# vmpmsuspend
vmpmsuspend_parser = domparser.add_parser('vmpmsuspend', help='suspend an active domain')
vmpmsuspend_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to suspend')
vmpmsuspend_parser.add_argument('-t', '--target', dest='target', action='store', default='mem', help='mem(Suspend-to-RAM), disk(Suspend-to-Disk), hybrid(Hybrid-Suspend)')

# vmpmwakeup
vmpmwakeup_parser = domparser.add_parser('vmpmwakeup', help='wakeup a domain previously suspended by dompmsuspend command')
vmpmwakeup_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to suspend')

# vminfo
vminfo_parser = domparser.add_parser('vminfo', help='show information associated to a domain')
vminfo_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain to query')

# vmcreate

# vmclone
vmclone_parser = domparser.add_parser('vmclone', help='clone a domaine')
vmclone_parser.add_argument('domain-name', action='store', help='name of a domain to clone')
vmclone_parser.add_argument('clone-name', action='store', help='name of a domain cloned')

# vmdelete
vmdelete_parser = domparser.add_parser('vmdelete', help='delete a domain')
vmdelete_parser.add_argument('domain-name', nargs='+', action='store', help='name of a domain')
vmdelete_parser.add_argument('-a', '--remove-all-storage', action='store_true', help='remove all associated storage volumes')
vmdelete_parser.add_argument('-s', '--storage', dest='storage', default=[], action='append', help='remove associated storage volumes')
vmdelete_parser.add_argument('-w', '--wipe-storage', action='store_true', help='wipe data on the removed volumes')
vmdelete_parser.add_argument('-m', '--snapshots-metadata', action='store_true', help='remove all domain snapshot metadata, if inactive')

##############################################################################
# Helpers
##############################################################################

def print_table(rows):
    widths = [ len(max(columns, key=len)) for columns in zip(*rows) ]
    header, data = rows[0], rows[1:]
    print('   '.join(format(title, "%ds" % width) for width, title in zip(widths, header)))
    print( '---'.join('-' * width for width in widths))
    for row in data:
        print("   ".join(format(cdata, "%ds" % width) for width, cdata in zip(widths, row)))

##############################################################################
# commands implementation
##############################################################################

def do_vmlist(params):
    # retrieve parameters
    drivers = params['uri']
    active_only = params['active_only']
    inactive_only = params['inactive_only']
    # process
    table = [['URI', 'Name', 'Status']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        if active_only:
            activedom = domm.list(DomainManager.ACTIVE)
            inactivedom = []
        elif inactive_only:
            activedom = []
            inactivedom = domm.list(DomainManager.INACTIVE)
        else:
            activedom = domm.list(DomainManager.ACTIVE)
            inactivedom = domm.list(DomainManager.INACTIVE)
        for dom in activedom:
            table.append([conn.uri, dom, 'active'])
        for dom in inactivedom:
            table.append([conn.uri, dom, 'inactive'])
    print_table(table)

def do_vmstate(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    # process
    table_success = [['URI', 'Name', 'State', 'State description']]
    table_fail = [['URI', 'Name', 'State', 'State description']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.state(domain)
            if result:
                table_success.append([conn.uri, domain, str(result[0]), result[1]])
            else:
                table_fail.append([conn.uri, domain, '', 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmstart(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    # process
    table_success = [['URI', 'Name', 'Status']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.start(domain)
            if result:
                table_success.append([conn.uri, domain, 'started'])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is already started'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmshutdown(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    force = params['force']
    mode = params['mode']
    # process
    table_success = [['URI', 'Name', 'Status', 'Forced', 'Mode']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            if force and mode == "gracefully":
                flags = DomainManager.STOP_FORCE_GRACEFUL
            elif not force and mode == "acpi":
                flags = DomainManager.STOP_ACPI
            elif not force and mode == "agent":
                flags = DomainManager.STOP_AGENT
            else:
                flags = 0
            result = domm.stop(domain, force, flags)
            if result:
                table_success.append([conn.uri, domain, 'shutdown', str(force), mode])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is already shutdown'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmautostart(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    disable = params['disable']
    # process
    table_success = [['URI', 'Name', 'Status']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.autostart(domain, False if disable else True)
            if result:
                table_success.append([conn.uri, domain, 'enabled' if not disable else 'disabled'])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or autostarted "{0}" already set'.format(disable)])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmreboot(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    mode = params['mode']
    # process
    table_success = [['URI', 'Name', 'Status', 'Mode']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            if mode == "acpi":
                flags = DomainManager.REBOOT_ACPI
            elif mode == "agent":
                flags = DomainManager.REBOOT_AGENT
            else:
                flags = 0
            result = domm.reboot(domain, flags)
            if result:
                table_success.append([conn.uri, domain, 'rebooted', mode])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is not active'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmreset(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    # process
    table_success = [['URI', 'Name', 'Status']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.reset(domain)
            if result:
                table_success.append([conn.uri, domain, 'resetted'])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is not started'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmresume(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    # process
    table_success = [['URI', 'Name', 'Status']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.resume(domain)
            if result:
                table_success.append([conn.uri, domain, 'resumed'])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is already active'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmsuspend(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    # process
    table_success = [['URI', 'Name', 'Status']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.suspend(domain)
            if result:
                table_success.append([conn.uri, domain, 'suspended'])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is already active'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmscreenshot(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    screen = params['screen']
    filename = params['filename']
    # process
    table_success = [['URI', 'Name', 'Screen', 'Status', 'Filename']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            result = domm.screenshot(domain, filename, screen)
            if result:
                table_success.append([conn.uri, domain, str(screen), 'screenshotted', result])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is not active'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmcoredump(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    filename = params['filename']
    mode = params['mode']
    # process
    table_success = [['URI', 'Name', 'Status', 'Mode', 'Filename']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            if mode == "reset":
                flags = DomainManager.DUMP_RESET
            elif mode == "crash":
                flags = DomainManager.DUMP_CRASH
            elif mode == "live":
                flags = DomainManager.DUMP_LIVE
            elif mode == "bypass-cache":
                flags = DomainManager.DUMP_BYPASS_CACHE
            result = domm.coredump(domain, filename, flags)
            if result:
                table_success.append([conn.uri, domain, 'coredumped', mode, result])
            elif result == None:
                table_fail.append([conn.uri, domain, 'domain does not exist or is shutdown'])
            else:
                table_fail.append([conn.uri, domain, 'error when querying this domain'])
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

def do_vmmemdump(params):
    # retrieve parameters
    level = params['level']
    drivers = params['uri']
    domains = params['domain-name']
    filename = params['filename']
    start = params['base']
    size = params['size']
    mode = params['mode']
    # process
    table_success = [['URI', 'Name', 'Status', 'Mode', 'Start', 'Size', 'Filename']]
    table_fail = [['URI', 'Name', 'Error']]
    for driver in drivers:
        try:
            conn = ConnectionManager(driver)
        except ConnectionManagerError as e:
            print('E: Unable to connect to "{0}": {1}'.format(driver, e))
            continue
        domm = DomainManager(conn)
        for domain in domains:
            if mode == "physical":
                flags = DomainManager.MEMORY_PHYSICAL
            elif mode == "virtual":
                flags = DomainManager.MEMORY_VIRTUAL
            if not filename:
                file = tempfile.NamedTemporaryFile(suffix='.bin', delete=False)
            else:
                file = open(filename, 'wb')
            remaining = size
            while remaining:
                bcount = remaining if remaining < 64 * 1024 else 64 * 1024
                len, data = domm.memdump(domain, start + size - remaining, bcount, flags)
                if len:
                    table_success.append([conn.uri, domain, 'memdumped', mode, str(start + size - remaining), str(bcount), file.name])
                elif data == None:
                    table_fail.append([conn.uri, domain, 'domain does not exist or is shutdown'])
                else:
                    table_fail.append([conn.uri, domain, 'error when querying this domain'])
                file.write(data)
                remaining -= len
            file.close()
    print_table(table_success)
    if level > 2:
        print("")
        print_table(table_fail)

##############################################################################
# dispatch commands
##############################################################################
command_dict = {
    'vmlist'        : do_vmlist,
    'vmstate'       : do_vmstate,
    'vmstart'       : do_vmstart,
    'vmshutdown'    : do_vmshutdown,
    'vmautostart'   : do_vmautostart,
    'vmreboot'      : do_vmreboot,
    'vmreset'       : do_vmreset,
    'vmresume'      : do_vmresume,
    'vmsuspend'     : do_vmsuspend,
    'vmscreenshot'  : do_vmscreenshot,
    'vmcoredump'    : do_vmcoredump,
    'vmmemdump'     : do_vmmemdump,
}

##############################################################################
# main
##############################################################################
if __name__ == '__main__':
    args = vars(parser.parse_args())
    subcommand = args.pop('subcommand', None)
    if subcommand:
        if command_dict.has_key(subcommand) and command_dict[subcommand]:
            command_dict[subcommand](args)
        else:
            raise NotImplementedError("subcommand '{0}' not yet implemented".format(subcommand))
