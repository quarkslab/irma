#
# Copyright (c) 2013-2016 Quarkslab.
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

""" Wrapper for hashlib cryptographic hash

One should use this module instead of hashlib
"""
import hashlib


# ====================
#  Helper / decorator
# ====================

def generic_sum(algorithm):
    """compute digest based on algorithm passed in parameter

    :param algorithm: hashlib algorithm to use
    :return: digest returned by the algorithm
    """

    def hash_sum(filename):
        """compute digest by chunks multiple of the block_size

        :param filename: name of the file from which we get data
        """
        handle = algorithm()
        with open(filename, 'rb') as fds:
            for chunk in iter(lambda: fds.read(128 * handle.block_size), b''):
                handle.update(chunk)
        return handle.hexdigest()
    return hash_sum


# ==========================
#  declare digest functions
# ==========================

md5sum = generic_sum(hashlib.md5)
"""use ``generic_sum`` to compute md5 digest"""
sha1sum = generic_sum(hashlib.sha1)
"""use ``generic_sum`` to compute sha1 digest"""
sha224sum = generic_sum(hashlib.sha224)
"""use ``generic_sum`` to compute sha224 digest"""
sha256sum = generic_sum(hashlib.sha256)
"""use ``generic_sum`` to compute sha256 digest"""
sha384sum = generic_sum(hashlib.sha384)
"""use ``generic_sum`` to compute sha384 digest"""
sha512sum = generic_sum(hashlib.sha512)
"""use ``generic_sum`` to compute sha512 digest"""
