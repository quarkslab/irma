"""Simple database interface"""
import leveldb
from leveldict import LevelDict


error = leveldb.LevelDBError


class LevelDbm(LevelDict):
    """LevelDB DBM-style wrapper"""
    def close(self):
        pass


def open(path, flag='r', mode=600):
    kwargs = {'create_if_missing': (flag == 'c')}
    return LevelDbm(path, **kwargs)


__all__ = ['open', 'error', 'LevelDbm']
