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

import logging

from lib.plugins import PluginManager

class IrmaFormatter:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, class_):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        manager = PluginManager()
        manager.discover("frontend/formatters", "frontend.formatters")
        self.formatters = manager.get_all_plugins()

    @classmethod
    def format(cls, probe_name, raw_result):
        
        # ========
        #  Helper 
        # ========
        def guess_mapping(probe_name):
            antivirus = ['ClamAV', 'ComodoCAVL', 'EsetNod32', 'FProt', 
                         'Kaspersky', 'McAfeeVSCL', 'Sophos', 'Symantec']
            metadata = ['StaticAnalyzer']
            database = ['NSRL', 'Nsrl']
            external = ['VirusTotal']

            if probe_name in antivirus:
                return "antivirus"
            elif probe_name in metadata:
                return "metadata"
            elif probe_name in database:
                return "database"
            elif probe_name in external:
                return "external"
            else:
                return "unknown"

        # Check if an error occured
        if not raw_result['success']:
            return {'error': raw_result['reason']}

        # get formatted results
        res = None
        for formatter in cls().formatters:
            if formatter.can_handle_results(raw_result):
                res = formatter.format(raw_result)
                logging.info("Using formatter {0} for raw results: {1}"
                              "".format(formatter.plugin_name, res))
                break
        # fallback to default formatter
        else:
            res = raw_result
            # FIXME: hack to handle old result format
            guessed_category = guess_mapping(probe_name)
            res['category'] = raw_result['metadata'].get('category', 
                                                         guessed_category)
            logging.warn("No formatter found, using default formatter: {1}"
                         "".format(formatter.plugin_name, res))
        return res
