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

from lib.plugins import PluginBase


class VirusTotalFormatterPlugin(PluginBase):

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "VirusTotal"
    _plugin_author_ = "IRMA (c) Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = "external"
    _plugin_description_ = "VirusTotal results Formatter"
    _plugin_dependencies_ = []

    # ===========
    #  Formatter
    # ===========

    @staticmethod
    def can_handle_results(raw_result):
        expected_name = VirusTotalFormatterPlugin.plugin_name
        expected_category = VirusTotalFormatterPlugin.plugin_category
        return raw_result.get('type', None) == expected_category and \
            raw_result.get('name', None) == expected_name

    """
    VT AVs list
    'Bkav', 'MicroWorld-eScan', 'nProtect', 'K7AntiVirus', 'NANO-Antivirus',
    'F-Prot', 'Norman', 'Kaspersky', 'ByteHero', 'F-Secure', 'TrendMicro',
    'McAfee-GW-Edition', 'Sophos', 'Jiangmin', 'ViRobot', 'Commtouch',
    'AhnLab-V3', 'VBA32', 'Rising', 'Ikarus', 'Fortinet', 'Panda',
    'CAT-QuickHeal', 'McAfee', 'Malwarebytes', 'K7GW', 'TheHacker',
    'TotalDefense', 'TrendMicro-HouseCall', 'Avast', 'ClamAV', 'BitDefender',
    'Agnitum', 'Comodo', 'DrWeb', 'VIPRE', 'AntiVir', 'Emsisoft', 'Antiy-AVL',
    'Kingsoft', 'Microsoft', 'SUPERAntiSpyware', 'GData', 'ESET-NOD32',
    'AVG', 'Baidu-International', 'Symantec', 'PCTools',
    """
    @staticmethod
    def format(raw_result):
        status = raw_result.get('status', -1)
        vt_result = raw_result.get('results', {})
        av_result = vt_result.get('results', {})
        if status == 1:
            # get ratios from virustotal results
            nb_detect = av_result.get('positives', 0)
            nb_total = av_result.get('total', 0)
            raw_result['results'] = "detected by {0}/{1}" \
                                    "".format(nb_detect, nb_total)
            # get antivirus results
            av_probes = ['ClamAV', 'Kaspersky', 'Symantec', 'McAfee',
                         'Sophos', 'Comodo', 'ESET-NOD32', 'F-Prot']
            results = filter(lambda (k, v): k in av_probes,
                             av_result.get('scans', {}).items())
            results = dict(map(lambda (k, v): (k, v.get('result', None)),
                               results))
            raw_result.update(results)
        elif status == 0:
            raw_result['results'] = av_result.get('verbose_msg', None)
        return raw_result
