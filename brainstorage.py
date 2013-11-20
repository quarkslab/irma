import gridfs
import uuid
from bson import ObjectId
from pymongo import MongoClient

dbh = None
def __dbconn():
   client = MongoClient('mongodb://192.168.130.133:27017/')
   db = client.irma_test_database
   return gridfs.GridFS(db)  
      
def store_file(data):
   if not dbh:
      dbh = __dbconn()
   oid = str(dbh.put(data))
   return oid
   
def get_file(oid):
   if not dbh:
      dbh = __dbconn()
   return dbh.get(ObjectId(oid)).read()
      


