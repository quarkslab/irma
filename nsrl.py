import hashlib
import leveldb
from lib.irma.common.exceptions import IrmaDatabaseError
import binascii

NSRL_DB = "/home/irma/nsrldb"

global db
db = leveldb.LevelDB(NSRL_DB, block_cache_size=1 << 30, max_open_files=3000)

def get_info(sha1):
    global db
    res = db.Get(binascii.unhexlify(sha1))
    return eval(res)

def scan(sfile):
    res = {}
    sha1 = hashlib.sha1(sfile.data).hexdigest()
    res['result'] = get_info(sha1)
    return res
