import hashlib
from pymongo import MongoClient
from lib.irma.common.exceptions import IrmaDatabaseError

class NsrlInfo(object):
    _uri = "mongodb://localhost:27017/"
    _dbname = "nsrl"
    _collection = "hashset"

    def __init__(self):
        self._dbh = None

    def _connect(self):
        try:
            if not self._dbh:
                print "DEBUG: mongo connection"
                client = MongoClient(self._uri)
                dbh = client[self._dbname]
                self._dbh = dbh[self._collection]
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))


    def get_info(self, sha1):
        try:
            self._connect()
            res = self._collection.find_one({'SHA-1':sha1}, {'_id': False})
            if not res:
                return 'Not found'
            return res
        except Exception as e:
            raise IrmaDatabaseError("{0}".format(e))

nsrlinfo = NsrlInfo()

def scan(sfile):
    res = {}
    sha1 = hashlib.sha1(sfile.data).hexdigest()
    res['result'] = nsrlinfo.get_info(sha1.upper())
    return res
