import brainstorage
from celery import Celery

celery=Celery('braintasks')
celery.config_from_object('celery_brainconfig')

@celery.task
def ping():
    return 1
        
@celery.task(serializer='pickle')
def scan(oid):
   size = len(brainstorage.get_file(oid).decode("base64"))
   return size
        

