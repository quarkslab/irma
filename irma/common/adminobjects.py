import re
from lib.irma.machine.libvirt_manager import LibVirtMachineManager
from lib.irma.common.exceptions import IrmaAdminError

class Node(LibVirtMachineManager):
    """ currently using libvirt to manage vms """
    def __init__(self, node_cs):
        self._probes = []
        self._node_cs = node_cs
        super(Node, self).__init__(node_cs)

    def get_probes(self):
        self._probes = []
        for label in self.list(self.INACTIVE):
            self._probes.append(Probe(label, self._node_cs, Probe.halted))
        for label in self.list(self.ACTIVE):
            self._probes.append(Probe(label, self._node_cs, Probe.running))
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
        if len(self.nodes_cs) != 0:
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
        n = Node(p.node)
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
        n = Node(p.node)
        n.clone(label, dstlabel)
        np = Probe(dstlabel, p.node, Probe.halted)
        self.probes.append(np)
        return "%s clone of %s added on node %s" % (np.label, p.label, np.node)

    def node_list(self):
        # refresh list and state of each probe by directly connect to node
        return self.nodes_cs
