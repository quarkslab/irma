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


class IrmaProbeType:
    unknown = 0
    antivirus = 1
    information = 2
    external = 3
    label = {unknown:     "unknown",
             antivirus:   "antivirus",
             information: "information",
             external:    "external",
             }
    mapping = {
        # Antivirus
        'ClamAV':     antivirus,
        'ComodoCAVL': antivirus,
        'EsetNod32':  antivirus,
        'FProt':      antivirus,
        'Kaspersky':  antivirus,
        'McAfeeVSCL': antivirus,
        'Sophos':     antivirus,
        'Symantec':   antivirus,
        # Information
        'StaticAnalyzer':   information,
        # External
        'Nsrl':         external,
        'VirusTotal':   external,
        }

    @staticmethod
    def get_type(probe_name):
        probe_type = IrmaProbeType.mapping.get(probe_name,
                                               IrmaProbeType.unknown)
        return IrmaProbeType.label[probe_type]


class IrmaFormatter:
    @staticmethod
    def format(probe_name, raw_result):
        formatter = IrmaFormatter.mapping.get(probe_name,
                                              IrmaFormatter.format_default)
        res = formatter(raw_result)
        res['type'] = IrmaProbeType.get_type(probe_name)
        if 'metadata' in raw_result and 'duration' in raw_result['metadata']:
            res['duration'] = raw_result['metadata']['duration']
        else:
            res['duration'] = "not available"
        return res

    @staticmethod
    def format_av(raw_result):
        output = {}
        if 'data' in raw_result:
            data = raw_result['data']
            if 'scan_results' in data:
                temp_list = data['scan_results'].values()
                if len(temp_list) > 1:
                    # if multiple output, filter None results
                    temp = [item for item in temp_list if item is not None]
                    output['result'] = " - ".join(temp)
                else:
                    output['result'] = temp_list[0]
            else:
                output['result'] = "not parsed"
            if 'name' in data:
                if 'version' in data:
                    name = data['name']
                    version = data['version']
                    output['version'] = "{0} ({1})".format(name, version)
                else:
                    output['version'] = data['name']
        else:
            output['result'] = "Error"
        return output

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
    def format_vt(raw_result):
        output = {}
        if 'data' in raw_result:
            data = raw_result['data'].values()[0]
            if type(data) is int:
                output['result'] = "error {0}".format(data)
            if 'response_code' in data and data['response_code'] == 0:
                output['result'] = "file never scanned"
            if 'scans' in data:
                scan = data['scans']
                for av in ['ClamAV', 'Kaspersky', 'Symantec', 'McAfee',
                           'Sophos', 'Comodo', 'ESET-NOD32', 'F-Prot']:
                    if av in scan:
                        output[av] = scan[av]['result']
                if 'positives' in data and data['positives'] > 0:
                    nb_detect = data['positives']
                    nb_total = data['total']
                    ratio = "{0}/{1}".format(nb_detect, nb_total)
                    output['result'] = "detected by {0}".format(ratio)
                else:
                    output['result'] = None
            if 'scan_date' in data:
                output['version'] = data['scan_date']
        else:
            output['result'] = "Error"
        return output

    @staticmethod
    def format_default(raw_result):
        output = {}
        if 'data' in raw_result:
            output = raw_result['data'].values()[0]
        else:
            output = raw_result
        return output

    @staticmethod
    def no_format(raw_result):
        return raw_result

IrmaFormatter.mapping = {
        # Antivirus
        'ClamAV':     IrmaFormatter.format_av,
        'ComodoCAVL': IrmaFormatter.format_av,
        'EsetNod32':  IrmaFormatter.format_av,
        'FProt':      IrmaFormatter.format_av,
        'Kaspersky':  IrmaFormatter.format_av,
        'McAfeeVSCL': IrmaFormatter.format_av,
        'Sophos':     IrmaFormatter.format_av,
        'Symantec':   IrmaFormatter.format_av,
        # Information
        'Nsrl':             IrmaFormatter.no_format,
        'StaticAnalyzer':   IrmaFormatter.format_default,
        # External
        'VirusTotal': IrmaFormatter.format_vt,
        }
