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
    """ On some systems, time.time() returns an int
    instead of a float. This function always returns a float
    rounded at 2 decimals

    :rtype: float
    :return: the current timestamp
    """
    return round(time.time(), 2)
