import time
import brainstorage
from celery import Celery,exceptions
from sonde import sondetasks

celery=Celery('braintasks')
celery.config_from_object('celeryconfig')

IRMA_TIMEOUT=10

@celery.task
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

'''      
@celery.task(serializer='pickle')
def scan(oid):
   try:   
      task = sondetasks.sonde_scan.delay(oid)        
      while not task.ready():
         time.sleep(1)
      res = task.get(timeout=IRMA_TIMEOUT)
   except exceptions.TimeoutError:
      res = "Sonde is down"
   return res
'''

@celery.task(serializer='pickle')
def scan(oid):
   try:   
      archfile = libarchive.Archive('my_archive.zip')
      oidlist = []
      for entry in archfile:
          oid = brainstorage.store_file(archfile.read())
          oidlist.append(oid)
      archfile.close()
      tasklist = []
      for oid in oidlist:
         task = sondetasks.sonde_scan.delay(oid)
      while tasklist:
         t = tasklist.pop()
         if not t.ready():
            tasklist.append(t)
            time.sleep(0.1)
         else:
            res += t.get(timeout=IRMA_TIMEOUT)
   except exceptions.TimeoutError:
      res = "Sonde is down"
   return res
           

