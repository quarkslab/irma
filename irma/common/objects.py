import re
from datetime import datetime
import config.dbconfig as dbconfig
from lib.irma.database.objects import DatabaseObject
from lib.irma.machine.libvirt_manager import LibVirtMachineManager
from lib.irma.common.exceptions import IrmaAdminError

class AttributeDictionary(dict):
    """A dictionnary with object-like accessors"""

    __getattr__ = lambda obj, key: obj.get(key, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class ScanStatus:
    init = 10
    launched = 11
    finished = 20
    cancelling = 30
    cancelled = 31

    label = {
             init:"scan created",
             launched:"scan launched",
             finished:"scan finished",
             cancelled:"scan cancelled"
    }

class ScanInfo(DatabaseObject):
    # TODO add date"
    # TODO add accounting
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_SCANINFO

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.user = None
        self.date = datetime.now()
        self.oids = {}
        self.taskid = None
        self.probelist = []
        self.status = ScanStatus.init
        super(ScanInfo, self).__init__(_id=_id)

    def get_results(self):
        res = {}
        for (oid, name) in self.oids.items():
            r = ScanResults(_id=oid)
            res[name] = dict((k, v) for (k, v) in r.results.iteritems() if k in self.probelist)
        return res

class ScanResults(DatabaseObject):
    _dbname = dbconfig.DB_NAME
    _collection = dbconfig.COLL_SCANRES

    def __init__(self, dbname=None, _id=None):
        if dbname:
            self._dbname = dbname
        self.probelist = []
        self.results = {}
        super(ScanResults, self).__init__(_id=_id)

class Node(LibVirtMachineManager):
    """ currently using libvirt to manage vms """
    def __init__(self, node_cs):
        self._probes = []
        self._node_cs = node_cs
        super(Node, self).__init__(node_cs)

    def get_probes(self):
        for label in self.list(self.INACTIVE):
            self._probes.append(Probe(label, self._node_cs, self.INACTIVE))
        for label in self.list(self.ACTIVE):
            self._probes.append(Probe(label, self._node_cs, self.ACTIVE))
        return self._probes


class Probe(object):
    halted = 0
    running = 1
    status_str = ["halted", "running"]

    def __init__(self, label, node, status):
        self.label = label
        self.node = node
        self.status = status

    @property
    def pstatus(self):
        return self.status_str[self.status]

class System(object):
    IRMA_MASTER_PREFIX = "master"

    def __init__(self, nodes_cs=[]):
        """ init system with nodes connection string list """
        self.probes = []
        self.nodes_cs = nodes_cs
        if self.nodes_cs:
            self._refresh()
        return

    def _refresh(self):
        res = []
        for node_cs in self.nodes_cs:
            n = Node(node_cs)
            res += n.get_probes()
        self.probes = res
        return

    def probe_is_master(self, probe):
        return re.search(self.IRMA_MASTER_PREFIX, probe.label)

    def _master_list(self):
        return [p for p in self.probes if self.probe_is_master(p)]

    def _probe_list(self):
        return [p for p in self.probes if not self.probe_is_master(p)]

    def _probe_lookup(self, node, label, master_lookup=False):
        # look for probe with label specified
        # node is optional if label is unique
        self._refresh()
        if not master_lookup and label in [p.label for p in self._master_list()]:
            raise IrmaAdminError("Can not use {0}: master image (clone it first)".format(label))
        if not node:
            t = filter(lambda x: x.label == label, self.probes)
        else:
            t = filter(lambda x: x.label == label and x.node == node, self.probes)
        if not t:
            raise IrmaAdminError("Probe {0} not found".format(label))
        elif len(t) != 1:
            raise IrmaAdminError("More than one Probe {0}".format(label))
        else:
            return t.pop()

    def _probe_set_state(self, node, label, state):
        p = self._probe_lookup(node, label)
        n = Node(driver=p.node)
        if state == Probe.halted:
            n.stop(p.label)
        if state == Probe.running:
            n.start(p.label)
        p.status = state
        return "node %s on %s %s" % (p.label, p.node, p.pstatus)

    def probe_list(self):
        # refresh list and state of each probe by directly connect to node
        self._refresh()
        res = {}
        for probe in self._probe_list():
            res[probe.node] = res.get(probe.node, []) + [(probe.label, probe.pstatus)]
        return res

    def probe_master_list(self):
        # refresh list and state of each probe masters by directly connect to node
        self._refresh()
        res = {}
        for probe in self._master_list():
            res[probe.node] = res.get(probe.node, []) + [(probe.label, probe.pstatus)]
        return res

    def probe_start(self, node, label):
        return self._probe_set_state(node, label, Probe.running)

    def probe_stop(self, node, label):
        return self._probe_set_state(node, label, Probe.halted)

    def probe_clone(self, node, label, dstlabel):
        p = self._probe_lookup(node, label, master_lookup=True)
        n = Node(driver=p.node)
        n.clone(label, dstlabel)
        np = Probe(dstlabel, p.node, Probe.halted)
        self.probes.append(np)
        return "%s clone of %s added on node %s" % (np.label, p.label, np.node)

    def node_list(self):
        # refresh list and state of each probe by directly connect to node
        return self.node_cs

