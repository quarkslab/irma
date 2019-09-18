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

from configparser import ConfigParser, NoOptionError
from http.cookies import SimpleCookie
from datetime import datetime

from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugins import ModuleDependency, FileDependency
from irma.common.plugin_result import PluginResult
from irma.common.base.utils import IrmaProbeType


class ICAPPlugin(PluginBase):

    class ICAPResult:
        ERROR = -1
        INFECTED = 0
        CLEAN = 1

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "ICAP"
    _plugin_display_name_ = "ICAP"
    _plugin_author_ = "Vincent Rasneur <vrasneur@free.fr>"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.external
    _plugin_description_ = "Plugin to query an ICAP antivirus server"
    _plugin_dependencies_ = [
        ModuleDependency(
            'icapclient',
            help='See requirements.txt for needed dependencies'
        ),
        FileDependency(
            os.path.join(os.path.dirname(__file__), 'config.ini')
        )
    ]

    # =============
    #  constructor
    # =============

    def __init__(self, **kwargs):
        # load default configuration file
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        self.conn_kwargs = self.retrieve_options(config, kwargs,
                                                 (('host', str),
                                                  ('port', int)))
        self.req_kwargs = self.retrieve_options(config, kwargs,
                                                (('service', str),
                                                 ('url', str),
                                                 ('timeout', int)))
        self.module = sys.modules['icapclient']

    @staticmethod
    def retrieve_options(config, kwargs, keys):
        options = {}

        # override default values if specified
        for option, type_ in keys:
            value = kwargs.get(option)
            if value is None:
                try:
                    value = config.get('ICAP', option)
                except NoOptionError:
                    pass
            if value is not None:
                options[option] = type_(value)

        return options

    def query_server(self, filename):
        conn = self.module.ICAPConnection(**self.conn_kwargs)
        conn.request('REQMOD', filename, read_content=False, **self.req_kwargs)
        resp = conn.getresponse()
        conn.close()

        # look for the headers defined inside
        # the RFC Draft for ICAP Extensions
        threat = resp.get_icap_header('X-Violations-Found')
        # multiple threats? try to parse the header values
        if threat is not None:
            try:
                values = threat.split('\n')
                # only read the human readable descriptions
                threats = [s.strip() for idx, s
                           in enumerate(values[1:]) if idx % 4 == 1]
                threat = '%s threat(s) found: %s' % \
                         (threats[0].strip(), ', '.join(threats))
            except:
                threat = 'Multiple threats found: %s' % threat
        if threat is None:
            # only a description
            threat = resp.get_icap_header('X-Virus-ID')
            if threat is not None:
                threat = 'Threat found: %s' % threat
        if threat is None:
            threat = resp.get_icap_header('X-Infection-Found')
            if threat is not None:
                # only return the human readable threat name
                cookie = SimpleCookie(threat)
                kv = cookie.get('Threat')
                if kv is not None:
                    threat = kv.value
            if threat is not None:
                threat = 'Threat found: %s' % threat

        return threat

    # ==================
    #  probe interfaces
    # ==================

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_display_name,
                               type=type(self).plugin_category,
                               version=None)
        try:
            # query the ICAP server: issue a REQMOD request
            started = timestamp(datetime.utcnow())
            response = self.query_server(paths)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            if response is None:
                results.status = self.ICAPResult.CLEAN
                results.results = 'No threat found'
            else:
                results.status = self.ICAPResult.INFECTED
                results.results = response
        except Exception as e:
            results.status = self.ICAPResult.ERROR
            results.error = type(e).__name__ + " : " + str(e)
        return results
