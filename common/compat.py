""" Helpers for python 2 and python 3 compatibility

This file should be imported in all modules
"""

import sys
import time


if sys.version_info >= (3,):
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


def timestamp():
    """ On some systems, time.time() returns a float
    instead of an int. This function always returns an int

    :rtype: int
    :return: the current timestamp
    """
    return int(time.time())