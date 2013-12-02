import celery
from celery.task import group
from brain import brainstorage
from sonde import sondetasks
from config.config import IRMA_TIMEOUT

celery_brain= celery.Celery('braintasks')
celery_brain.config_from_object('config.brainconfig')
bstorage = brainstorage.BrainStorage()

@celery_brain.task(name="brain.scan", ignore_result=True)
def scan(scanid, oids):
   # create one subtask per oid to scan per antivirus queue
   tasks = []
   avlist = ['kaspersky','clamav']
   for oid in oids:
      for av in avlist:
         tasks.append(sondetasks.sonde_scan.si(args=[scanid,oid],queue=av))
   job = group(tasks).apply_async()
   job.save()
   bstorage.update_scan_record(scanid,{'taskid':job.id , 'avlist':avlist})
   return

