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

        
@celery.task(serializer='pickle')
def scan(oid):
   try:   
      task = sondetasks.scan.delay()        
      while not task.ready():
         time.sleep(1)
      res = task.get(timeout=IRMA_TIMEOUT)
   except exceptions.TimeoutError:
      res = "Sonde is down"
   return res
        

