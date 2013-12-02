import gridfs
import uuid
from bson import ObjectId
import pymongo
import hashlib
import copy
from config.config import MONGODB

RESCOLL = "res"
SCANCOLL = "scan"
FSFILESCOLL = "fs.files"

class BrainStorage(object):

   def __init__(self):
      self.dbh = None
      self.hash = hashlib.sha256
      return

   def __dbconn(self, collection_name=None):
      """ connect if needed to the database and returns a dbhandler to the collection specified """
      if not self.dbh:
         client = pymongo.MongoClient(MONGODB)
         self.dbh = client.irma_test
      if collection_name:
         return self.dbh[collection_name]
      return

   def __create_update_record(self, collection_name, oid, update):
      """ update record with update dict"""
      dbh = self.__dbconn(collection_name)
      record = dbh.find_one({'_id':ObjectId(oid)})
      if not record:
         print "DEBUG New result object created"
         record=dict({'_id':ObjectId(oid)})
      for key, value in update.items():
         record[key] = value
      print "DEBUG Update with ",record
      dbh.save(record)
      return

#______________________________________________________________ FILE API

   def store_file(self, data, name=None):
      """ put data into gridfs and get file object-id """
      dbh = self.__dbconn(FSFILESCOLL)
      fsdbh = gridfs.GridFS(self.dbh)
      datahash = self.hash(data).hexdigest()
      # Check if hash is already present in db
      fr = dbh.find_one({'hexdigest':datahash})
      if fr:
         # if yes return the existing file_oid
         return str(fr['_id'])
      else:
         # if not create a new record
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

   def update_scan_record(self, scan_oid, update):
      self.__create_update_record(SCANCOLL, scan_oid, update)
      return

   def get_scan_fileoid(self,scan_oid):
      """ get list of file oids associated with scanid """
      dbh = self.__dbconn(SCANCOLL)
      record = dbh.find_one({"_id":ObjectId(scan_oid)})
      return record['oids']

   def get_scan_results(self,scan_oid):
      """ get list of file oids associated with scanid """
      dbh = self.__dbconn(SCANCOLL)
      record = dbh.find_one({"_id":ObjectId(scan_oid)})
      res = {}
      for (file_oid,filename) in record['oids'].items():
         res[filename] = self.get_result(file_oid)
      return res

   def get_scan_taskid(self,scan_oid):
      """ get list of file oids associated with scanid """
      dbh = self.__dbconn(SCANCOLL)
      scan = dbh.find_one({"_id":ObjectId(scan_oid)})
      if 'taskid' in scan:
         return scan['taskid']
      else:
         return None
#______________________________________________________________ RESULTS API

   def update_result(self, file_oid, update):
      """ put result from sonde into resultdb and link with  """
      self.__create_update_record(RESCOLL, file_oid, update)
      return

   def get_result(self,file_oid):
      """ get list of results associated with scanid """
      dbh = self.__dbconn(RESCOLL)
      return dbh.find_one({'_id':ObjectId(file_oid)},{'_id': False})

   def get_result_nb(self, file_oids, avlist):
      dbh = self.__dbconn(RESCOLL)
      oids = map(lambda o: ObjectId(o), file_oids)
      res = 0
      for r  in dbh.find({'_id': {'$in': oids}}, {'_id': False}):
         res += len(filter(lambda a: a in avlist, r.keys()))
      return res



