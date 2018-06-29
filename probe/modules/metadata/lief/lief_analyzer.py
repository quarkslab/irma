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

import json


class LIEFAnalyzer(object):
    def __init__(self):
        global lief
        import lief
        self.version = lief.__version__

    @staticmethod
    def analyze(filepath):
        res = lief.parse(filepath)
        json_res = lief.to_json(res)
        return json.loads(json_res)

    def get_version(self):
        return self.version
