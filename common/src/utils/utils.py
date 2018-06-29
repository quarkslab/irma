#
# Copyright (c) 2013-2018 Quarkslab.
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

import uuid
import re
import random
import collections
from time import mktime
import urllib.request
import urllib.parse
import urllib.error
from functools import reduce


class UUID(object):

    pattern = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',
                         re.IGNORECASE)

    @classmethod
    def validate(cls, val):
        try:
            uuid.UUID(val)
        except Exception:
            return False
        return True

    @classmethod
    def generate(cls):
        return str(uuid.uuid4())

    @classmethod
    def normalize(cls, val):
        return str(uuid.UUID(val))


class MAC(object):

    pattern = re.compile(r'[0-9a-f]{2}(:[0-9a-f]{2}){5}', re.IGNORECASE)

    @classmethod
    def validate(cls, val):
        if MAC.pattern.match(val.strip()):
            return True
        return False

    @classmethod
    def generate(cls, oui=None):
        if not oui or \
            len(oui) != 3 or \
            not reduce(lambda x, y: x and y,
                       [isinstance(x, int) for x in oui]):
            # Xensource, Inc.
            oui = [0x00, 0x16, 0x3e]
        mac = []
        mac.extend([x % 255 for x in oui])
        mac.extend([random.randint(0x00, 0x7f),
                    random.randint(0x00, 0xff),
                    random.randint(0x00, 0xff)])
        return ':'.join(["%02x" % x for x in mac])

    @classmethod
    def normalize(cls, val):
        return str(val)


def timestamp(date):
    return mktime(date.timetuple()) + date.microsecond / 1000000.0


def bytes_to_utf8(data):
    if isinstance(data, bytes):
        data = data.decode("utf-8")
        return data
    elif isinstance(data, str):
        return data
    elif isinstance(data, collections.Mapping):
        return dict(list(map(bytes_to_utf8, list(data.items()))))
    elif isinstance(data, collections.Iterable):
        return type(data)(list(map(bytes_to_utf8, data)))
    else:
        return data


def decode_utf8(utf8_str):
    return urllib.parse.unquote(utf8_str)


def save_to_file(fileobj, dst_path, chunk_size=2 ** 20):
    size = 0
    fileobj.seek(0)
    with open(dst_path, "wb") as dst:
        while 1:
            buf = fileobj.read(chunk_size)
            if not buf:
                break
            dst.write(buf)
            size += len(buf)
    fileobj.seek(0)
    return size
