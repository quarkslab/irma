from config.adminconfig import admin_celery
from lib.irma.database.objects import IrmaConfig
from lib.irma.common.utils import IrmaTaskReturn

# ______________________________________________________________ GLOBAL TASKS

@admin_celery.task()
def shutdown():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def start():
    return IrmaTaskReturn.success("To be done")


# ______________________________________________________________ NODE TASKS

@admin_celery.task()
def get_all_nodes():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def add_node():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def del_node():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def get_node_by_probe_type():
    return IrmaTaskReturn.success("To be done")

# ______________________________________________________________ PROBE TASKS

@admin_celery.task()
def add_probe():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def del_probe():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def start_probe():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def stop_probe():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def delete_probe():
    return IrmaTaskReturn.success("To be done")

@admin_celery.task()
def get_probe_by_type():
    return IrmaTaskReturn.success("To be done")

