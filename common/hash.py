import hashlib


# ====================
#  Helper / decorator
# ====================

def generic_sum(algorithm):
    def hash_sum(filename):
        handle = algorithm()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * handle.block_size), b''):
                handle.update(chunk)
        return handle.hexdigest()
    return hash_sum

##############################################################################
# declare sums
##############################################################################

md5sum = generic_sum(hashlib.md5)
sha1sum = generic_sum(hashlib.sha1)
sha224sum = generic_sum(hashlib.sha224)
sha256sum = generic_sum(hashlib.sha256)
sha384sum = generic_sum(hashlib.sha384)
sha512sum = generic_sum(hashlib.sha512)
