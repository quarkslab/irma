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

import os
import sys
import re

from datetime import datetime
from configparser import ConfigParser

from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugins import ModuleDependency, FileDependency
from irma.common.plugins import PluginLoadError
from irma.common.plugin_result import PluginResult
from irma.common.utils.hash import sha1sum
from irma.common.base.utils import IrmaProbeType
from functools import reduce


class NSRLPlugin(PluginBase):

    class NSRLPluginResult:
        ERROR = -1
        FOUND = 1
        NOT_FOUND = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "NSRL"
    _plugin_display_name_ = "National Software Reference Library"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.database
    _plugin_description_ = "Information plugin to query hashes on " \
                           "NRSL database"
    _plugin_dependencies_ = [
        ModuleDependency(
            'leveldict',
            help='See requirements.txt for needed dependencies'
        ),
        ModuleDependency(
            'modules.database.nsrl.nsrl'
        ),
        FileDependency(
            os.path.join(os.path.dirname(__file__), 'config.ini')
        )
    ]
    _plugin_mimetype_regexp = 'PE32'

    @classmethod
    def verify(cls):
        # load default configuration file
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        os_db = config.get('NSRL', 'nsrl_os_db')
        mfg_db = config.get('NSRL', 'nsrl_mfg_db')
        file_db = config.get('NSRL', 'nsrl_file_db')
        prod_db = config.get('NSRL', 'nsrl_prod_db')
        databases = [os_db, mfg_db, file_db, prod_db]

        # check for configured database path
        results = list(map(os.path.exists, databases))
        dbs_available = reduce(lambda x, y: x or y, results, False)
        if not dbs_available:
            raise PluginLoadError("{0}: verify() failed because "
                                  "databases are not available."
                                  "".format(cls.__name__))

        # check for LOCK file and remove it
        dbs_locks = [os.path.join(x, "LOCK") for x in databases]
        for lock in dbs_locks:
            try:
                if os.path.exists(lock):
                    os.unlink(lock)
            except:
                raise PluginLoadError("unable to remove lock {0}".format(lock))

    # ==================================
    #  constructor and destructor stuff
    # ==================================

    def __init__(self):
        # load default configuration file
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        # get configuration values
        nsrl_os_db = config.get('NSRL', 'nsrl_os_db')
        nsrl_mfg_db = config.get('NSRL', 'nsrl_mfg_db')
        nsrl_file_db = config.get('NSRL', 'nsrl_file_db')
        nsrl_prod_db = config.get('NSRL', 'nsrl_prod_db')

        # lookup module
        module = sys.modules['modules.database.nsrl.nsrl'].NSRL

        self.module = module(nsrl_file_db, nsrl_prod_db,
                             nsrl_os_db, nsrl_mfg_db)

    # ==================
    #  probe interfaces
    # ==================

    def run(self, paths):
        results = PluginResult(name=type(self).display_name,
                               type=type(self).plugin_category,
                               version=None)
        try:
            # lookup the specified sha1
            started = timestamp(datetime.utcnow())
            response = self.module.lookup_by_sha1(sha1sum(paths).upper())
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            # check for errors
            if isinstance(response, dict) and \
                (not response.get('MfgCode', None) or
                 not response.get('OpSystemCode', None) or
                 not response.get('ProductCode', None) or
                 not response.get('SHA-1', None)):
                results.status = self.NSRLPluginResult.NOT_FOUND
                response = None
            else:
                results.status = self.NSRLPluginResult.FOUND
            results.results = response
        except Exception as e:
            results.status = self.NSRLPluginResult.ERROR
            results.error = type(e).__name__ + " : " + str(e)
        return results
