from celery import Celery
import brainstorage
import time

celery=Celery('braintasks')
celery.config_from_object('celeryconfig')

@celery.task
def ping():
    return 1
        
@celery.task(serializer='pickle')
def scan(oid):
   size = len(brainstorage.get_file(oid).decode("base64"))
   return size
        

