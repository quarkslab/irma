from config.adminconfig import admin_celery
from lib.irma.common.utils import IrmaTaskReturn
from lib.irma.common.adminobjects import System
from lib.irma.common.exceptions import IrmaAdminError


system = System(nodes_cs=['qemu+tcp://192.168.130.1/system'])

# ______________________________________________________________ NODE TASKS

@admin_celery.task()
def list_nodes():
    try:
        return IrmaTaskReturn.success(system.list_nodes())
    except Exception, e:
        return IrmaTaskReturn.error(str(e))

# ______________________________________________________________ PROBE TASKS

@admin_celery.task()
def probe_list():
    try:
        return IrmaTaskReturn.success(system.probe_list())
    except Exception, e:
        return IrmaTaskReturn.error(str(e))

@admin_celery.task()
def probe_master_list():
    try:
        return IrmaTaskReturn.success(system.probe_master_list())
    except Exception, e:
        return IrmaTaskReturn.error(str(e))

@admin_celery.task()
def probe_clone(node, label, dstlabel):
    try:
        return IrmaTaskReturn.success(system.probe_clone(node, label, dstlabel))
    except Exception, e:
        return IrmaTaskReturn.error(str(e))

@admin_celery.task()
def del_probe():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def probe_start(node, label):
    try:
        return IrmaTaskReturn.success(system.probe_start(node, label))
    except Exception, e:
        return IrmaTaskReturn.error(str(e))

@admin_celery.task()
def probe_stop(node, label):
    try:
        return IrmaTaskReturn.success(system.probe_stop(node, label))
    except Exception, e:
        return IrmaTaskReturn.error(str(e))

