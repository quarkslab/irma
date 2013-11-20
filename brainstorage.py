import gridfs
import uuid
from bson import ObjectId
from pymongo import MongoClient

        
class BrainStorage(object):
   _instance = None
   def __new__(cls, *args, **kwargs):
      if not cls._instance:
         cls._instance = super(BrainStorage, cls).__new__(
                          cls, *args, **kwargs)
      return cls._instance
        
   def __init__(self):
      self.dbh = None
      return
      
   def __dbconn(self):
      print "New Client"
      client = MongoClient('mongodb://192.168.130.133:27017/')
      db = client.irma_test_database
      self.dbh = gridfs.GridFS(db)  
         
   def store_file(self,data):
      if not self.dbh:
         self.__dbconn()
      oid = str(self.dbh.put(data))
      return oid
      
   def get_file(self,oid):
      if not self.dbh:
         self.__dbconn()
      return self.dbh.get(ObjectId(oid)).read()
      


