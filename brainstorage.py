import gridfs
import uuid
from bson import ObjectId
import pymongo
import hashlib

        
class BrainStorage(object):
   GRIDFS_DB = "irma_test_database"
   
   def __init__(self):
      self.dbh = None
      self.hash = hashlib.sha256
      return
      
   def __dbconn(self):
      client = pymongo.MongoClient('mongodb://192.168.130.133:27017/')
      db = client.GRIDFS_DB
      self.dbh = gridfs.GridFS(db)  
      return 
         
   def store_file(self,data, name=None, date_lastresult=None):
      """ put data into gridfs and get file object-id """
      if not self.dbh:
         self.__dbconn()
      datahash = self.hash(data).hexdigest()
      oid = str(self.dbh.put(data, filename=name, hexdigest=datahash, date_lastresult=date_lastresult))
      return oid
      
   def get_file(self,oid):
      """ get data from gridfs by file object-id """
      if not self.dbh:
         self.__dbconn()
      return self.dbh.get(ObjectId(file_oid))

