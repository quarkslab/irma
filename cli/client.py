import time
import celery
from brain import braintasks, brainstorage
from config.config import IRMA_TIMEOUT
from celery.result import TaskSetResult
import signal

bstorage = brainstorage.BrainStorage()

class Ticket:
   def __init__(self, asres, param):
      self.asres=asres
      self.param=param
      return
   
   def ready(self):
      return self.asres.ready()
    
   def result(self):
      if not self.ready():
         return "Not ready"
      return self.asres.get()

   def cancel(self):
      self.asres.revoke(terminate=True,signal=signal.SIGINT)
      return

def scan(filenames):
   """ send a filename to the brain for scanning """
   tickets=[]
   for filename in filenames:
      data = open(filename,"rb").read()
      oid = bstorage.store_file(data.encode("base64"))
      # create one subtask per oid to scan
      task = braintasks.scan.delay(oid)
      tickets.append(Ticket(task,filename))
   return tickets

def export(filename,oid):
   """ retrieve a file previously sent to the brain """
   bstorage = brainstorage.BrainStorage()
   data = bstorage.get_file(oid)
   open(filename,"wb").write(data.decode("base64"))
   print "File with oid %s exported in %s"%(oid,filename)

def status():
   """ check if brain is up and running """
   task = braintasks.ping.delay()
   try:
      print task.get(timeout=IRMA_TIMEOUT)
   except celery.exceptions.TimeoutError:
      print "Brain down"
   return
