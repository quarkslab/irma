from config.adminconfig import admin_celery
from lib.irma.common.utils import IRMA_RETCODE_OK, IRMA_RETCODE_WARNING, IRMA_RETCODE_ERROR
from lib.irma.database.objects import ScanInfo, ScanResults
from config.dbconfig import launched, finished, cancelled, SCAN_STATUS_INIT, cancelling

def success(info):
    return (IRMA_RETCODE_OK, info)

def warning(info):
    return (IRMA_RETCODE_WARNING, info)

def error(info):
    return (IRMA_RETCODE_ERROR, info)

# ______________________________________________________________ GLOBAL TASKS

@admin_celery.task()
def shutdown():
    return success("To be done")

@admin_celery.task()
def start():
    return success("To be done")


# ______________________________________________________________ NODE TASKS

@admin_celery.task()
def get_all_nodes():
    return success("To be done")

@admin_celery.task()
def add_node():
    return success("To be done")

@admin_celery.task()
def del_node():
    return success("To be done")

@admin_celery.task()
def get_node_by_sonde_type():
    return success("To be done")

# ______________________________________________________________ SONDE TASKS

@admin_celery.task()
def add_sonde():
    return success("To be done")

@admin_celery.task()
def del_sonde():
    return success("To be done")

@admin_celery.task()
def start_sonde():
    return success("To be done")

@admin_celery.task()
def stop_sonde():
    return success("To be done")

@admin_celery.task()
def delete_sonde():
    return success("To be done")

@admin_celery.task()
def get_sonde_by_type():
    return success("To be done")

