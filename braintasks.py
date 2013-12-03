import celery
from celery.task import group
from brain import brainstorage
from sonde import sondetasks
from config.config import IRMA_TIMEOUT,SCAN_STATUS_LAUNCHED,SCAN_STATUS_FINISHED,SCAN_STATUS_CANCELLED


celery_brain= celery.Celery('braintasks')
celery_brain.config_from_object('config.brainconfig')
bstorage = brainstorage.BrainStorage()

@celery_brain.task(ignore_result=True)
def scan(scanid, oids):
   tasks = []
   avlist = ['clamav','kaspersky']
   for oid in oids:
      for av in avlist:
         # create one subtask per oid to scan per antivirus queue
         tasks.append(sondetasks.sonde_scan.subtask(args=(scanid,oid), options={'queue':av}))
   job = group(tasks)
   res = job.apply_async()
   # keep the groupresult object for task status/cancel
   res.save()
   bstorage.update_scan_record(scanid,{'status':SCAN_STATUS_LAUNCHED, 'taskid':res.id , 'avlist':avlist})
   return

@celery_brain.task(ignore_result=True)
def scan_finished(scanid):
   bstorage.update_scan_record(scanid,{'status':SCAN_STATUS_FINISHED})
   return

@celery_brain.task(ignore_result=True)
def scan_cancel(scanid):
   bstorage.update_scan_record(scanid,{'status':SCAN_STATUS_CANCELLED})
   return
