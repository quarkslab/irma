import gridfs
import uuid
from bson import ObjectId
import pymongo
import hashlib
import copy

RESCOLL = "res"
SCANCOLL = "scan"
     
class BrainStorage(object):

   
   def __init__(self):
      self.dbh = None
      self.hash = hashlib.sha256
      return
      
   def __dbconn(self, collection_name=None):
      if not self.dbh:
         client = pymongo.MongoClient('mongodb://192.168.130.133:27017/')
         self.dbh = client.irma_test
      if collection_name:
         return self.dbh[collection_name]
      return
      
   def __update_record(self, collection_name, oid, update):
      """ update scan record with update """      
      dbh = self.__dbconn(collection_name)
      record = dbh.find_one({'_id':ObjectId(oid)})
      for key, value in update.items():
         record[key] = value
      dbh.save(record)
      return
     
#______________________________________________________________ FILE API
              
   def store_file(self, data, name=None):
      """ put data into gridfs and get file object-id """
      self.__dbconn()
      fsdbh = gridfs.GridFS(self.dbh)        
      datahash = self.hash(data).hexdigest()
      file_oid = fsdbh.put(data, filename=name, hexdigest=datahash)
      return str(file_oid)
      
   def get_file(self,file_oid):
      """ get data from gridfs by file object-id """
      self.__dbconn()
      fsdbh = gridfs.GridFS(self.dbh)        
      return fsdbh.get(ObjectId(file_oid))

   def get_file_data(self,file_oid):
      """ get data from gridfs by file object-id """
      return self.get_file(file_oid).read()

#______________________________________________________________ SCAN API

   def create_scan_record(self, file_oids):
      dbh = self.__dbconn(SCANCOLL)
      scan_oid = dbh.save({'oids': file_oids, 'avlist':[], 'nblaunched': 0, 'nbsuccess':0 })
      return str(scan_oid)

   def update_scan_record(self, scan_oid, avlist, nbscan):      
      self.__update_record(SCANCOLL, scan_oid, {'avlist':avlist, 'nblaunched':nbscan})
      return

   def get_scan_fileoid(self,scan_oid):
      """ get list of file oids associated with scanid """
      dbh = self.__dbconn(SCANCOLL)
      record = dbh.find_one({"_id":ObjectId(scan_oid)})
      return record['oids']
   
#______________________________________________________________ RESULTS API   
   
    
   def create_result(self, file_oid, result):
      """ put result from scan into resultdb and link with file_oid """
      dbh = self.__dbconn(RESCOLL)
      result['_id']=file_oid
      dbh.save(result)
      return

   def update_result(self, file_oid, update):
      """ put result from sonde into resultdb and link with  """
      self.__update_record(RESCOLL, file_oid, update)
      return
      
 
   def get_results_from_fileoid(self,file_oids):
      """ get list of results associated with scanid """
      dbh = self.__dbconn(RESCOLL)
      res = {}
      for file_oid in file_oids:     
         res.append(dbh.find_one({"_id":file_oid}))
      return record
   

      
   
      
