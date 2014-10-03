#
# Copyright (c) 2013-2014 QuarksLab.
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

import config.parser as config
from lib.irma.database.nosqlobjects import NoSQLDatabaseObject
from frontend.helpers.format import IrmaFormatter

cfg_dburi = config.get_db_uri()
cfg_dbname = config.frontend_config['mongodb'].dbname
cfg_coll = config.frontend_config['collections']


cfg_coll_prefix = '{0}_'.format(config.get_nosql_db_collections_prefix())


class ProbeRealResult(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = '{0}probe_real_result'.format(cfg_coll_prefix)

    def __init__(self,
                 name=None,
                 type=None,
                 version=None,
                 status=None,
                 duration=None,
                 results=None,
                 dbname=None,
                 **kwargs):
        if dbname:
            self._dbname = dbname
        self.name = name
        self.type = type
        self.version = version
        self.status = status
        self.duration = duration
        self.results = results
        super(ProbeRealResult, self).__init__(**kwargs)

    def get_results(self, formatted):
            res = self.to_dict()
            res.pop("_id")
            # apply or not IrmaFormatter
            if formatted:
                res = IrmaFormatter.format(self.name, res)
            return res
