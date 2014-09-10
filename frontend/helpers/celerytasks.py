import celery
from lib.irma.common.exceptions import IrmaTaskError


def sync_call(celery_app, taskpath, taskname, timeout, **kwargs):
    """ send a task to the celery app with specified args
        and wait until timeout param for result
    """
    try:
        full_task_path = "{0}.{1}".format(taskpath, taskname)
        task = celery_app.send_task(full_task_path, **kwargs)
        (status, res) = task.get(timeout=timeout)
        return (status, res)
    except celery.exceptions.TimeoutError:
        raise IrmaTaskError("Celery timeout - {0}".format(taskname))


def async_call(celery_app, taskpath, taskname, **kwargs):
    """ send a task to the celery app with specified args
        without waiting for results.
    """
    try:
        full_task_path = "{0}.{1}".format(taskpath, taskname)
        celery_app.send_task(full_task_path, **kwargs)
    except:
        raise IrmaTaskError("Celery error - {0}".format(taskname))
