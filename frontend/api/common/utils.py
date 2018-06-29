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

import re
import os

import config.parser as config
from irma.common.utils.utils import UUID
from irma.common.base.exceptions import IrmaValueError, IrmaFileSystemError


def validate_id(ext_id):
    """ check external_id format - should be a str(ObjectId)"""
    if not UUID.validate(ext_id):
        raise ValueError("Malformed id")


def validate_sha256(sha256):
    """ check hashvalue format - should be a sha256 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{64}$', sha256):
        raise ValueError("Malformed sha256")


def validate_sha1(sha1):
    """ check hashvalue format - should be a sha1 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{40}$', sha1):
        raise ValueError("Malformed sha1")


def validate_md5(md5):
    """ check hashvalue format - should be a md5 hexdigest"""
    if not re.match(r'^[0-9a-fA-F]{32}$', md5):
        raise ValueError("Malformed md5")


def guess_hash_type(value):
    """ guess which kind of hash is given as parameter """
    hash_type = None

    # We use hash length as hash index to speed up lookups
    hash_dict = {
        32: ("md5", validate_md5),
        40: ("sha1", validate_sha1),
        64: ("sha256", validate_sha256),
    }

    str_length = len(str(value))
    if str_length in hash_dict.keys():
        validate = hash_dict[str_length][1]
        hash_str = hash_dict[str_length][0]
        try:
            validate(value)
            hash_type = hash_str
        except ValueError:
            pass
    return hash_type


# helper to split files in subdirs
def build_sha256_path(sha256):
    """Builds a file path from its sha256. Creates directory if needed.
    :param sha256: the sha256 to create path
    :rtype: string
    :return: the path build from the sha256
    :raise: IrmaValueError, IrmaFileSystemError
        """
    PREFIX_NB = 3
    PREFIX_LEN = 2
    base_path = config.get_samples_storage_path()
    if (PREFIX_NB * PREFIX_LEN) > len(sha256):
        raise IrmaValueError("too much prefix for file storage")
    path = base_path
    for i in range(0, PREFIX_NB):
        prefix = sha256[i * PREFIX_LEN: (i + 1) * PREFIX_LEN]
        path = os.path.join(path, prefix)
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isdir(path):
        reason = "storage path is not a directory"
        raise IrmaFileSystemError(reason)
    return os.path.join(path, sha256)
