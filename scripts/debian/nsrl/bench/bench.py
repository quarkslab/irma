#!/usr/bin/env python

import sys
import random
import timeit

if len(sys.argv) != 3:
    print "Usage %s <nsrl_leveldb_dir> <existing_keys_set>"%sys.argv[0]
    sys.exit(1)

db_dir = sys.argv[1]
key_file = sys.argv[2]

f =  open(key_file,"r").read()
keys = f.split(',')
    
def my_setup(db,keys):
    return """
import leveldb
from binascii import unhexlify,hexlify

def read():
	dbdir = \"%s\"
	keys = %r
	db = leveldb.LevelDB(dbdir, block_cache_size = 1 << 30, max_open_files=3000)
	for k in keys:
		db.Get(unhexlify(k))
	return
"""%(db,keys)

print "Sequencial read %d keys:"%len(keys)
t = timeit.Timer(stmt="read()", setup=my_setup(db_dir,keys[0:10000]))
print (t.repeat(repeat=3, number=10))

random.shuffle(keys)
print "Random read %d keys:"%len(keys)
t = timeit.Timer(stmt="read()", setup=my_setup(db_dir,keys[0:10000]))
print(t.repeat(repeat=3, number=10))

