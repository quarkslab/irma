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
