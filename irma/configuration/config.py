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

class AttributeDictionary(dict):
    """A dictionnary with object-like accessors"""

    __getattr__ = lambda obj, key: obj.get(key, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Configuration(AttributeDictionary):
    pass


class ConfigurationSection(Configuration):
    pass
