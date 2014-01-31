import hashlib
import leveldb
import binascii

NSRL_DB = "/home/irma/nsrldb"

global db
db = leveldb.LevelDB(NSRL_DB, block_cache_size=1 << 30, max_open_files=3000)

def get_info(sha1):
    global db
    try:
        res = eval(db.Get(binascii.unhexlify(sha1)))
    except KeyError:
        res = "Not found"
    return res

def scan(sfile):
    res = {}
    sha1 = hashlib.sha1(sfile.data).hexdigest()
    res['result'] = get_info(sha1)
    return res
