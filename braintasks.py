import time
import brainstorage
import libarchive
from celery import Celery,exceptions
from sonde import sondetasks

celery=Celery('braintasks')
celery.config_from_object('config.brainconfig')

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

@celery.task(serializer='pickle')
def scan(oid):
   task = sondetasks.sonde_scan.delay(oid)        
   return task

@celery.task(serializer='pickle')
def scanarchive(oid):
   try:   
      data = brainstorage.get_file(oid)
      archfile = libarchive.Archive(data)
      oidlist = []
      for entry in archfile:
          print "Unzip",entry.pathname
          oid = brainstorage.store_file(archfile.read())
          oidlist.append(oid)
          time.sleep(1)
      archfile.close()
      tasklist = []
      for oid in oidlist:
         task = sondetasks.sonde_scan.delay(oid)
         time.sleep(0.1)
      while tasklist:
         print "Tasklist contains: %d",len(tasklist)
         t = tasklist.pop()
         if not t.ready():
            tasklist.append(t)
            time.sleep(1)
         else:
            res += t.get(timeout=IRMA_TIMEOUT)
   except exceptions.TimeoutError:
      res = "Sonde is down"
   return res
           

