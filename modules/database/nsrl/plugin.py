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

import os
import sys

from ConfigParser import SafeConfigParser

from lib.plugins import PluginBase
from lib.plugins import ModuleDependency, FileDependency
from lib.plugins import PluginLoadError
from lib.plugin_result import PluginResult
from lib.common.hash import sha1sum


class NSRLPlugin(PluginBase):

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "NSRL"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = "database"
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

    @classmethod
    def verify(cls):
        # load default configuration file
        config = SafeConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        os_db = config.get('NSRL', 'nsrl_os_db')
        mfg_db = config.get('NSRL', 'nsrl_mfg_db')
        file_db = config.get('NSRL', 'nsrl_file_db')
        prod_db = config.get('NSRL', 'nsrl_prod_db')
        databases = [os_db, mfg_db, file_db, prod_db]

        # check for configured database path
        results = map(os.path.exists, databases)
        dbs_available = reduce(lambda x, y: x or y, results, False)
        if not dbs_available:
            raise PluginLoadError("database are not available")

        # check for LOCK file and remove it
        dbs_locks = map(lambda x: os.path.join(x, "LOCK"), databases)
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
        config = SafeConfigParser()
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
        # allocate plugin results place-holders
        plugin_results = PluginResult(type(self).plugin_name)
        # launch an antivirus scan, automatically append scan results to
        # antivirus.results.
        plugin_results.start_time = None
        results = self.module.lookup_by_sha1(sha1sum(paths).upper())
        plugin_results.end_time = None
        # allocate memory for data, and fill with data
        plugin_results.data = {paths: results}
        return plugin_results.serialize()
