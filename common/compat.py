import sys

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

