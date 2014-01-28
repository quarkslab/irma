import logging, libvirt, xmltodict, tempfile, mimetypes, os.path

from lib.common import compat
from lib.common.utils import UUID, MAC
from lib.common.oopatterns import ParametricSingleton

from lib.virt.core.storage_pool import StoragePoolManager
from lib.virt.core.storage_volume import StorageVolumeManager

from lib.virt.core.connection import ConnectionManager
from lib.virt.core.exceptions import DomainManagerError

log = logging.getLogger(__name__)

class DomainManager(ParametricSingleton):
    """Domain manager to a manage a domain on a local or remote virtual machine manager"""

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
            raise DomainManagerError("'connection' field type '{0}' is not valid".format(type(handler)))

        try:
            uri = handler.getURI()
        except libvirt.libvirtError as e:
            raise DomainManagerError("unable to get domain uri from connection handle")
        return uri

    ##########################################################################
    # constants
    ##########################################################################

    # Available state
    ACTIVE = 1
    INACTIVE = 2

    # Available status
    NOSTATE = libvirt.VIR_DOMAIN_NOSTATE
    RUNNING = libvirt.VIR_DOMAIN_RUNNING
    BLOCKED = libvirt.VIR_DOMAIN_BLOCKED
    PAUSED = libvirt.VIR_DOMAIN_PAUSED
    SHUTDOWN = libvirt.VIR_DOMAIN_SHUTDOWN
    SHUTOFF = libvirt.VIR_DOMAIN_SHUTOFF
    CRASHED = libvirt.VIR_DOMAIN_CRASHED
    PMSUSPENDED = libvirt.VIR_DOMAIN_PMSUSPENDED

    # start flags
    START_PAUSED = libvirt.VIR_DOMAIN_START_PAUSED              # Launch guest in paused state
    START_AUTODESTROY = libvirt.VIR_DOMAIN_START_AUTODESTROY    # Automatically kill guest when virConnectPtr is closed
    START_BYPASS_CACHE = libvirt.VIR_DOMAIN_START_BYPASS_CACHE  # Avoid file system cache pollution
    START_FORCE_BOOT = libvirt.VIR_DOMAIN_START_FORCE_BOOT      # Boot, discarding any managed save

    # stop (not forced) flags
    STOP_ACPI = libvirt.VIR_DOMAIN_SHUTDOWN_ACPI_POWER_BTN      # Send ACPI event
    STOP_AGENT = libvirt.VIR_DOMAIN_SHUTDOWN_GUEST_AGENT        # Use guest agent

    # stop (forced) flags
    STOP_FORCE_GRACEFUL = libvirt.VIR_DOMAIN_DESTROY_GRACEFUL   # only SIGTERM, no SIGKILL

    # reboot flags
    REBOOT_ACPI = libvirt.VIR_DOMAIN_REBOOT_ACPI_POWER_BTN      # Send ACPI event
    REBOOT_AGENT = libvirt.VIR_DOMAIN_REBOOT_GUEST_AGENT        # Use guest agent

    # coredump flags
    DUMP_CRASH = libvirt.VIR_DUMP_CRASH                         # crash after dump
    DUMP_LIVE = libvirt.VIR_DUMP_LIVE                           # live dump
    DUMP_BYPASS_CACHE = libvirt.VIR_DUMP_BYPASS_CACHE           # avoid file system cache pollution
    DUMP_RESET = libvirt.VIR_DUMP_RESET                         # reset domain after dump finishes

    # memdump flags
    MEMORY_VIRTUAL = libvirt.VIR_MEMORY_VIRTUAL                 # addresses are virtual addresses
    MEMORY_PHYSICAL = libvirt.VIR_MEMORY_PHYSICAL               # addresses are physical addresses

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, connection, prefetch=False):
        """Instantiate a domain manager for specified connection

        :param connection: either an instance of a ``ConnectionManager`` or directly a libvirt connection handler
        :param prefetch: set to True if prefetching domain handlers for this connection is required
        :raises: DomainManagerError if ``connection`` is not an expected type or None
        """
        if isinstance(connection, basestring):
            connection = ConnectionManager(connection)

        self._cache = {'name': {}, 'uuid': {}, 'id': {}}

        self._drv = connection
        if isinstance(self._drv, ConnectionManager):
            self._drv = self._drv.connection

        try:
            self._uri = self._drv.getURI()
        except libvirt.libvirtError as e:
            raise DomainManagerError("unable to get domain uri from connection handle")

        if prefetch:
            domains = self.list()
            for domain in domains:
                self.lookup(domain)

    ##########################################################################
    # context manager stuff
    ##########################################################################

    def __enter__(self):
        return self

    ##########################################################################
    # internal helpers
    ##########################################################################

    def _list_active(self):
        labels = list()
        try:
            ids = self._drv.listDomainsID()
            for id in ids:
                labels.append(self._drv.lookupByID(id).name())
        except libvirt.libvirtError as e:
            raise DomainManagerError("{0}".format(e))
        return tuple(labels)

    def _list_inactive(self):
        labels = list()
        try:
            labels.extend(self._drv.listDefinedDomains())
        except libvirt.libvirtError as e:
            raise DomainManagerError("{0}".format(e))
        return tuple(labels)

    def _cache_handle(self, cache, entry, where=None):
        if not isinstance(cache, dict):
            raise ValueError("'cache' fields must be a dict")
        if where and entry:
            for key, value in where.items():
                if key in cache:
                    cache[key][value] = entry

    def _lookupByID(self, id):
        # type checking
        if not isinstance(id, int):
            raise DomainManagerError("'id' field type '{0}' is not valid".format(type(id)))

        handle = None
        # check if domain has already been cached
        if id in self._cache['id']:
            handle = self._cache['id'][id]
        # domain not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.lookupByID(id)
                name = handle.name()
                uuid = handle.UUIDString()
                where = {'name': name, 'uuid': uuid}
                if handle.isActive():
                    where['id'] = id
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    def _lookupByName(self, name):
        # type checking
        if not isinstance(name, basestring):
            raise DomainManagerError("'name' field type '{0}' is not valid".format(type(name)))

        handle = None
        # check if domain has already been cached
        if name in self._cache['name']:
            handle = self._cache['name'][name]
        # domain not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.lookupByName(name)
                uuid = handle.UUIDString()
                where = {'name': name, 'uuid': uuid}
                # if handle is not active, id is not available
                if handle.isActive():
                    where['id'] = handle.ID()
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    def _lookupByUUID(self, uuid):
        # type checking
        if not isinstance(uuid, basestring) or not UUID.validate(uuid):
            raise DomainManagerError("'uuid' field '{0}' is not valid".format(uuid))

        handle = None
        # check if domain has already been cached
        if uuid in self._cache['uuid']:
            handle = self._cache['uuid'][uuid]
        # domain not in cache, retrieve and cache it
        else:
            try:
                handle = self._drv.lookupByUUID(uuid)
                name = handle.name()
                where = {'name': name, 'uuid': uuid}
                # if handle is not active, id is not available
                if handle.isActive():
                    where['id'] = res.ID()
                self._cache_handle(self._cache, handle, where)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        return handle

    def _lib_version(self):
        version = self._drv.getLibVersion()
        # version has the format major * 1,000,000 + minor * 1,000 + release.
        major = (version / 1000000)
        minor = (version % 1000000) / 1000
        release = version % 1000
        return (major, minor, release)

    ##########################################################################
    # public methods
    ##########################################################################

    def lookup(self, domain):
        handle = None
        if isinstance(domain, (tuple, list)):
            handle = list()
            for dom in domain:
                handle.append(self.lookup(dom))
            handle = tuple(handle)
        elif isinstance(domain, int):
            handle = self._lookupByID(domain)
        elif isinstance(domain, basestring):
            handle = self._lookupByName(domain)
            if not handle and UUID.validate(domain):
                handle = self._lookupByUUID(domain)
            if not handle and domain.isdigit():
                handle = self._lookupByID(int(domain))
            if not handle:
                log.warn("Unable to find domain {0} on {1}", domain, self._uri)
        return handle

    def list(self, filter=ACTIVE | INACTIVE):
        """list machines on this domain

        :param filter: either DomainManager.ACTIVE or DomainManager.INACTIVE 
               to respectively active or inactive machines
        :returns: a tuple containing domain names (w.r.t specified filter)
        """
        labels = list()

        # NOTE: virConnectListAllDomains is not binded in python, thus, we have
        # to use other way to list all machines
        filter = filter & (DomainManager.ACTIVE | DomainManager.INACTIVE)
        if not filter or filter & DomainManager.ACTIVE:
            labels.extend(self._list_active())
        if not filter or filter & DomainManager.INACTIVE:
            labels.extend(self._list_inactive())

        return tuple(labels)

    state_desc = {
        NOSTATE  : "no state",
        RUNNING  : "is running",
        BLOCKED  : "is blocked on resource",
        PAUSED   : "is paused by user",
        SHUTDOWN : "is being shut down",
        SHUTOFF  : "is shut off",
        CRASHED  : "is crashed",
        PMSUSPENDED : "is pm-suspended"
    }

    def state(self, domains):
        """get state of the machines specified via domains

        :param domains: either a label, uuid, id, virDomain object or a list
                        of label, uuid, id, a virDomain object.
        :returns: (state, a string description) tuple if domains is a label, a
                uuid, a id, a virDomain or a tuple of (state, a string
                description) if domains is a list. If an error (state, a
                string description) equals to (None, None).
        """
        result = (None, None)
        if isinstance(domains, libvirt.virDomain):
            try:
                # extra flags; not used yet, so callers should always pass 0
                state, reason = domains.state(flags=0)
                descr = DomainManager.state_desc[state]
                result = (state, descr)
            except libvirt.libvirtError as e:
                log.error('{0}'.format(e))
        elif isinstance(domains, (basestring, int)):
            result = self.state(self.lookup(domains))
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.state(domain))
            result = tuple(result)
        return result

    def start(self, domains, flags=0):
        """start specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :param flags: default flag if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a uuid,
                a id, a virDomain or a tuple if domains is a list. When domain
                is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and not domains.isActive():
                    domains.createWithFlags(flags)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                flags = domains.get('flags', flags)
                result = self.start(domain, flags)
        elif isinstance(domains, (basestring, int)):
            result = self.start(self.lookup(domains), flags)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.start(domain, flags))
            result = tuple(result)
        return result

    def stop(self, domains, force=False, flags=0):
        """stop specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :param force: default policy for force if not specified otherwise
        :param flags: default flag if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a uuid,
                a id, a virDomain or a tuple if domains is a list. When domain
                is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    if not force:
                        domains.shutdownFlags(flags)
                    else:
                        domains.destroyFlags(flags)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                flags = domains.get('flags', flags)
                force = domains.get('force', force)
                result = self.stop(domain, force, flags)
        elif isinstance(domains, (basestring, int)):
            result = self.stop(self.lookup(domains), force, flags)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.stop(domain, force, flags))
            result = tuple(result)
        return result

    def autostart(self, domains, autostart=True):
        """set autostart on specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to
                        specify flags) or a list of label, uuid, id, virDomain
                        object or a list of dict.
        :param autostart: default autostart value if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a
                  uuid, a id, a virDomain or a tuple if domains is a list. When
                  domain is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.autostart() != autostart:
                    domains.setAutostart(autostart)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                autostart = domains.get('autostart', autostart)
                result = self.autostart(domain, autostart)
        elif isinstance(domains, (basestring, int)):
            result = self.autostart(self.lookup(domains), autostart)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.autostart(domain, autostart))
            result = tuple(result)
        return result

    def reboot(self, domains, flags=0):
        """reboot specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :param flags: default flags value if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    domains.reboot(flags)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                autostart = domains.get('flags', flags)
                result = self.reboot(domain, flags)
        elif isinstance(domains, (basestring, int)):
            result = self.reboot(self.lookup(domains), flags)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.reboot(domain, flags))
            result = tuple(result)
        return result

    def reset(self, domains):
        """reset specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    # extra flags; not used yet, so callers should always pass 0
                    domains.reset(flags=0)
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                result = self.reset(domain)
        elif isinstance(domains, (basestring, int)):
            result = self.reset(self.lookup(domains))
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.reset(domain))
            result = tuple(result)
        return result

    def resume(self, domains):
        """resume specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and not domains.isActive():
                    # extra flags; not used yet, so callers should always pass 0
                    domains.resume()
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                result = self.resume(domain)
        elif isinstance(domains, (basestring, int)):
            result = self.reset(self.lookup(domains))
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.resume(domain))
            result = tuple(result)
        return result

    def suspend(self, domains):
        """suspend specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    # extra flags; not used yet, so callers should always pass 0
                    domains.suspend()
                    result = True
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                result = self.suspend(domain)
        elif isinstance(domains, (basestring, int)):
            result = self.suspend(self.lookup(domains))
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.suspend(domain))
            result = tuple(result)
        return result

    def screenshot(self, domains, name=None, screen=0):
        """perform screenshot on specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :param name: default name value if not specified otherwise
        :param screen: default screen value if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    stream = self._drv.newStream(flags=0)
                    # extra flags; not used yet, so callers should always pass 0
                    mime = domains.screenshot(stream, screen, flags=0)
                    if not name:
                        ext = mimetypes.guess_extension(mime) or '.ppm'
                        temp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                    else:
                        temp = open(name, 'wb')
                    stream.recvAll(lambda stream, data, fdes: fdes.write(data), temp)
                    stream.finish()
                    temp.close()
                    result = temp.name
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                name = domains.get('name', None)
                screen = domains.get('screen', screen)
                result = self.screenshot(domain, name, screen)
        elif isinstance(domains, (basestring, int)):
            result = self.screenshot(self.lookup(domains), name, screen)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.screenshot(domain), name, screen)
            result = tuple(result)
        return result

    def coredump(self, domains, name=None, flags=DUMP_LIVE):
        """perform a core dump on specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :param flags: default flags value if not specified otherwise
        :param name: default name value if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    if not name:
                        file = tempfile.NamedTemporaryFile(suffix='.bin', delete=False)
                        name = file.name
                        file.close()
                    domains.coreDump(name, flags)
                    result = name
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                name = domains.get('name', name)
                flags = domains.get('flags', flags)
                result = self.coredump(domain, name, flags)
        elif isinstance(domains, (basestring, int)):
            result = self.coredump(self.lookup(domains), name, flags)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.coredump(domain, name, flags))
            result = tuple(result)
        return result

    def memdump(self, domains, start=None, size=None, flags=MEMORY_PHYSICAL):
        result = (None, None)
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and domains.isActive():
                    if not start:
                        start = 0
                    if not size:
                        version = self._lib_version()
                        if version < (0, 9, 13):
                            size = 64 * 1024
                        elif version < (1, 0, 6):
                            size = 1 * 1024 * 1024
                        else:
                            size = 16 * 1024 * 1024
                    data = domains.memoryPeek(start, size, flags)
                    result = (len(data), data)
            except libvirt.libvirtError as e:
                result = (False, None)
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                start = domains.get('start', limit)
                size = domains.get('size', size)
                flags = domains.get('flags', flags)
                result = self.memdump(domain, start, size, flags)
        elif isinstance(domains, (basestring, int)):
            result = self.memdump(self.lookup(domains), start, size, flags)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.memdump(domain, start, size, flags))
            result = tuple(result)
        return result

    # TODO: add return value checking
    # TODO: autogenerate name and allow name to be none
    # TODO: allow not to clone disk, possible ?
    def clone(self, domains, name):
        """perform screenshot on specified domains

        :param domains: either a label, uuid, id, a virDomain, a dict (to specify flags) 
                        or a list of label, uuid, id, virDomain object or a list of dict.
        :param name: default name value if not specified otherwise
        :param screen: default screen value if not specified otherwise
        :returns: False if failed, True if success if domains is a label, a uuid,
                  a id, a virDomain or a tuple if domains is a list. When domain
                  is None, returns None.
        """
        if not name:
            raise DomainManagerError("'name' field value '{0}' is invalid".format(name))

        result = None
        if isinstance(domains, libvirt.virDomain):
            try:
                if domains and not domains.isActive():
                    orig_xml = domains.XMLDesc(0)
                    orig_dict = xmltodict.parse(orig_xml)

                    # modify configuration
                    new_dict = orig_dict
                    dom = self.lookup(name)
                    if dom:
                        raise DomainManagerError("domain '{0}' already exists".format(name))
                    while True:
                        uuid = UUID.generate()
                        if not self.lookup(uuid):
                            break
                    new_dict['domain']['name'] = name
                    new_dict['domain']['uuid'] = uuid
                    # TODO: handle multiple ethernet card
                    new_dict['domain']['devices']['interface']['mac']['@address'] = MAC.generate()
                    # TODO: handle if only one disk
                    for disk in new_dict['domain']['devices']['disk']:
                        if not disk['@device'] == 'disk':
                            continue
                        orig_filename = disk['source']['@file']
                        orig_ext = os.path.splitext(orig_filename)[1]
                        # TODO: use StorageVolumeManager here
                        orig_vol = self._drv.storageVolLookupByPath(orig_filename)
                        # TODO: what if the pool does not exist ?
                        orig_pool = orig_vol.storagePoolLookupByVolume()
                        vol_man = StorageVolumeManager(self._drv, orig_pool)
                        new_vol = vol_man.clone(orig_vol.name(), ''.join([name, orig_ext]))
                        disk['source']['@file'] = new_vol.path()
                    new_xml = xmltodict.unparse(new_dict)
                    self._drv.defineXML(new_xml)
            except libvirt.libvirtError as e:
                result = False
                log.error('{0}'.format(e))
        elif isinstance(domains, dict):
            if domains.has_key('domain'):
                domain = domains.get('domain', None)
                name = domains.get('name', None)
                result = self.clone(domain, name)
        elif isinstance(domains, (basestring, int)):
            result = self.clone(self.lookup(domains), name)
        elif isinstance(domains, (list, tuple)):
            result = list()
            for domain in domains:
                result.append(self.clone(domain), name)
            result = tuple(result)
        return result

    def delete(self, label, storage=None, wipe=False, managed_save=True, snapshot_metadata=True):
        # TODO: needs refactoring, more parameters handling
        try:
            machine = self.lookup(label)
            if machine.isActive():
                raise IrmaMachineManagerError("Cannot delete a running machine.")

            flags = 0
            # extra flags; not used yet, so callers should always pass 0
            if managed_save and machine.hasManagedSaveImage(flags=0):
                flags |= libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE

            # extra flags; not used yet, so callers should always pass 0
            if snapshot_metadata and machine.hasCurrentSnapshot(flags=0):
                flags |= libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA

            # Destroy volumes
            orig_xml = machine.XMLDesc(libvirt.VIR_DOMAIN_XML_INACTIVE)
            orig_dict = xmltodict.parse(orig_xml)
            for disk in orig_dict["domain"]["devices"]["disk"]:
                if not disk["@device"] == 'disk':
                    continue
                orig_vol = self._drv.storageVolLookupByPath(disk['source']['@file'])
                orig_vol.delete(flags)

            # Undefine
            machine.undefine()
        except libvirt.libvirtError as e:
            raise DomainManagerError("Couldn't delete virtual machine {0}: {1}".format(label, e))

    def info(self, label):
        # TODO: need refactoring, temporary
        try:
            domain = self.lookup(label)
            xml = domain.XMLDesc(0)
            return Domain.parse(xml)
        except libvirt.libvirtError as e:
            raise DomainManagerError(e)

    def create(self, domain):
        # TODO: need refactoring, temporary
        try:
            xml = domain.unparse()
            self._drv.defineXML(xml)
        except libvirt.libvirtError as e:
            raise DomainManagerError(e)
