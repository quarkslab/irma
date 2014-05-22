#
# Copyright (c) 2014 QuarksLab.
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
