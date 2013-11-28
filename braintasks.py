import time
import libarchive
from celery import Celery,exceptions
from celery.result import GroupResult
from celery.task import group
from sonde import sondetasks
from config.config import IRMA_TIMEOUT
from brain import brainstorage

celery_brain=Celery('braintasks')
celery_brain.config_from_object('config.brainconfig')
bstorage = brainstorage.BrainStorage()

@celery_brain.task(name="brain.scan")
def scan(scanid, oids):
   # create one subtask per oid to scan per antivirus queue
   tasks = []
   avlist = ['kaspersky','clamav']
   for oid in oids:
      for av in avlist:
         tasks.append(sondetasks.sonde_scan.s(args=[scanid,oid],queue=av))
   job = group(tasks).apply_async()
   job.save()
   print "DEBUG Group saved:",job.id
   bstorage.update_scan_record(scanid,avlist,len(avlist)*len(oids))
   return job.get()  

