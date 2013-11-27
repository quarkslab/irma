import gridfs
import uuid
from bson import ObjectId
import pymongo
import hashlib

        
class BrainStorage(object):
   DBNAME = "irma_test"
   RESCOLL = "results"
   SCANCOLL = "scan"

   def __init__(self):
      self.dbh = None
      self.hash = hashlib.sha256
      return
      
   def __dbconn(self):
      client = pymongo.MongoClient('mongodb://192.168.130.133:27017/')
      self.dbh = client.DBNAME
      return 
         
   def store_file(self,data, name=None , date_lastresult=None):
      """ put data into gridfs and get file object-id """
      if not self.dbh:
         self.__dbconn()
      fsdbh = gridfs.GridFS(self.dbh)        
      datahash = self.hash(data).hexdigest()
      oid = fsdbh.put(data, filename=name, hexdigest=datahash, date_lastresult=date_lastresult)
      return str(oid)
      
   def get_file(self,oid):
      """ get data from gridfs by file object-id """
      if not self.dbh:
         self.__dbconn()
      fsdbh = gridfs.GridFS(self.dbh)        
      return fsdbh.get(ObjectId(oid))


   def create_scan_record(self, oids):
      if not self.dbh:
         self.__dbconn()
      dbh = self.dbh.SCANCOLL
      oid = dbh.save({'oids':{oid:[] for oid in oids}})
      return str(oid)

   def get_scanid_oids(self,scan_oid):
      """ get list of oids associated with scanid """
      if not self.dbh:
         self.__dbconn()  
      dbh = self.dbh.SCANCOLL
      record = dbh.find_one({"_id":ObjectId(scan_oid)})
      return record['oids']
   
   def update_result(self,scan_oid, file_oid, result):
      """ put result from sonde into resultdb and link with scan """
      if not self.dbh:
         self.__dbconn()
      dbh = self.dbh.RESCOLL
      res_oid = str(dbh.save(result))
      dbh = self.dbh.SCANCOLL
      scan = dbh.find_one({'_id':ObjectId(scan_oid)})
      scan['oids'][file_oid].append(res_oid)
      dbh.save(scan)
      return
      
