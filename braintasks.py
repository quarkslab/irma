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

@celery_brain.task(name="brain.ping")
def ping():
   res = "Brain is up and running\n"
   try:   
      task = sondetasks.ping.delay()        
      while not task.ready():
         time.sleep(1)
      res += task.get(timeout=IRMA_TIMEOUT)
   except exceptions.TimeoutError:
      res += "Sonde is down"
   return res

@celery_brain.task(name="brain.scan")
def scan(scanid, oids):
   # create one subtask per oid to scan per antivirus queue
   tasks = []
   avlist = ['kaspersky','clamav']
   for oid in oids:
      for av in avlist:
         tasks.append(sondetasks.sonde_scan.subtask(args=[scanid,oid],queue=av))
   res = group(tasks).apply_async()
   bstorage.update_scan(scanid,{'avlist':avlist, 'nbscan':len(avlist)*len(oids)})
   return res.get()  
