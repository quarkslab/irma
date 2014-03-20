import sys
import time

if sys.version_info >= (3,):
    str = str                  #pragma: no cover
    unicode = str              #pragma: no cover
    bytes = bytes              #pragma: no cover
    basestring = (str,bytes)   #pragma: no cover
else:
    str = str                  #pragma: no cover
    unicode = unicode          #pragma: no cover
    bytes = str                #pragma: no cover
    basestring = basestring    #pragma: no cover

def timestamp():
    """ On some systems, time.time() returns a float instead of an int. This function always returns an int
    :rtype: int
    :return: the current timestamp
    """
    return int(str(time.time()).split('.')[0])