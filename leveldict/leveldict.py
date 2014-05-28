#
# Copyright (c) 2013-2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

"""LevelDB dict-like wrapper."""
import leveldb
import os.path

from copy import copy
from collections import MutableMapping


__all__ = ['LevelDict', 'LevelDictSerialized', 'LevelRoot']


class WriteBatchContext(object):
    """Context manager to handle batch writes."""

    def __init__(self, db):
        # wrap a copy of the db instance
        self._db = db
        self._batch = leveldb.WriteBatch()
        self._leveldb = db._db

    def _write(self):
        self._leveldb.Write(self._batch)

    def __enter__(self):
        # expose same db api but with overrided set/del methods
        # the returned wrapped instance lives within the context
        # created
        return self._wrap(copy(self._db))

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            self._write()

    def _wrap(self, db):
        """Overrides `db` put and delete methods"""
        def batch__put(key, value):
            self._batch.Put(key, value)
        db.__put = batch__put

        def batch__delete(key):
            self._batch.Delete(key)
        db.__delete = batch__delete

        return db


class LevelDict(MutableMapping):
    """LevelDB dict-style wrapper."""

    def __init__(self, db, **kwargs):
        if isinstance(db, basestring):
            db = leveldb.LevelDB(db, **kwargs)
        assert isinstance(db, leveldb.LevelDB), "db is not LevelDB instance"
        self._db = db

    def __copy__(self):
        """Create new LevelDict instance sharing the same LevelDB
        instance."""
        return type(self)(self._db)

    def write_batch(self):
        return WriteBatchContext(self)

    def __put(self, key, value):
        """Covenience method for overriding"""
        self._db.Put(key, value)

    def __delete(self, key):
        """Covenience method for overriding"""
        self._db.Delete(key)

    def __getitem__(self, key):
        return self._db.Get(self.__keytransform__(key))

    def __setitem__(self, key, value):
        self.__put(self.__keytransform__(key), value)

    def __delitem__(self, key):
        self.__delete(self.__keytransform__(key))

    def __iter__(self):
        return self.iterkeys()

    def __keytransform__(self, key):
        return key

    def __len__(self):
        raise NotImplementedError

    # expose RangeIter api
    def range(self, *args, **kwargs):
        return self._db.RangeIter(*args, **kwargs)

    # improved methods
    def iteritems(self):
        return self.range()

    def iterkeys(self):
        return self.range(include_value=False)

    def itervalues(self):
        for (k, v) in self.iteritems():
            yield v

    def keys(self):
        # fixes default method which calls __len__
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def has_key(self, key):
        return key in self

    def clear(self):
        # TODO: use leveldb.DestroyDB
        with self.write_batch() as wb:
            while True:
                try:
                    wb.popitem()
                except KeyError:
                    break

    def count(self):
        return sum(1 for key in self)


class LevelDictSerialized(LevelDict):
    """LevelDB dict-style wrapper with serialized values."""

    def __init__(self, db, serializer, **kwargs):
        LevelDict.__init__(self, db, **kwargs)
        self.serializer = serializer

    def __keytransform__(self, key):
        # for convenience, allow unicode keys and serialize.
        # although, keys doesn't get converted back to unicode
        # when accessing them through .keys(), .items(), etc.
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return key

    def __getitem__(self, key):
        value = LevelDict.__getitem__(self, key)
        return self.serializer.loads(value)

    def __setitem__(self, key, value):
        value = self.serializer.dumps(value)
        LevelDict.__setitem__(self, key, value)

    def __copy__(self):
        """Create new LevelDict instance sharing the same LevelDB
        instance."""
        return type(self)(self._db, serializer=self.serializer)

    def range(self, *args, **kwargs):
        """RangeIter-like method."""
        include_value = kwargs.get('include_value', True)
        _range = LevelDict.range
        if not include_value:
            return _range(self, *args, **kwargs)
        else:
            # can't return range output directly as is needed to
            # deserialize values
            return (
                (k, self.serializer.decode(v))
                for k, v in _range(self, *args, **kwargs)
            )


class LevelRoot(object):
    """Provides a dict-like interface to access multiple LevelDB instances."""

    leveldb_cls = LevelDict

    def __init__(self, root, **kwargs):
        kwargs.setdefault('create_if_missing', True)
        self.leveldb_cls = kwargs.pop('leveldb_cls', self.leveldb_cls)
        self.leveldb_kwargs = kwargs
        self.root = os.path.abspath(root)
        self.databases = {}

    def __getitem__(self, dbname):
        if dbname not in self.databases:
            self.databases[dbname] = self.leveldb_cls(
                os.path.join(self.root, dbname), **self.leveldb_kwargs
            )
        return self.databases[dbname]


# FIXME: make unit tests
__doc__ = """
>>> import tempfile, os
>>> root = tempfile.mkdtemp(prefix='leveldict-')

>>> levelroot = LevelRoot(root)
>>> db = levelroot['db1']
>>> db['a'] = 'foo'
>>> db['b'] = 'bar'
>>> db.items()
[('a', 'foo'), ('b', 'bar')]

>>> import json
>>> levelroot = LevelRoot(root,
                          leveldb_cls=LevelDictSerialized,
                          serializer=json)
>>> db = levelroot['db2']
>>> db['a'] = {'data': 1}
>>> db['b'] = ['foo', False, None]
>>> db.items()
[('a', {u'data': 1}), ('b', [u'foo', False, None])]
>>> with db.write_batch() as wb:
...     wb['c'] = None
...     del wb['b']
...     _ = wb.pop('a')
>>> db.items()
[('c', None)]

"""
