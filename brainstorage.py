import gridfs
import uuid
from bson import ObjectId
from pymongo import MongoClient
     
def __dbconn():
   client = MongoClient('mongodb://192.168.130.133:27017/')
   db = client.irma_test_database
   return gridfs.GridFS(db)  
      
def store_file(data):
   dbh = __dbconn()
   oid = str(dbh.put(data))
   return oid
   
def get_file(oid):
   dbh = __dbconn()
   return dbh.get(ObjectId(oid)).read()
      


