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


def format_av(output, result):
    if 'data' in result:
        data = result['data']
        if 'scan_results' in data:
            res_list = data['scan_results'].values()
            if len(res_list) > 1:
                # if multiple output, filter None results
                res = [item for item in res_list if item is not None]
                output['result'] = " - ".join(res)
            else:
                output['result'] = res_list[0]
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
    return


def format_vt(output, result):
    """ VT AVs list
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
    output['type'] = "web"
    if 'data' in result:
        data = result['data'].values()[0]
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
                output['result'] = "detected by {0}/{1}".format(nb_detect,
                                                                nb_total)
            else:
                output['result'] = None
        if 'scan_date' in data:
            output['version'] = data['scan_date']
    else:
        output['result'] = "Error"
    return


def format_static(output, result):
    output['type'] = "information"
    if 'data' in result:
        data = result['data'].values()[0]
        if type(data) == dict:
            output['result'] = None
            output['info'] = data
        else:
            output['result'] = "no results"
    else:
        output['result'] = "not a PE file"
    output['version'] = None
    return


def format_nsrl(output, _):
    output['type'] = "database"
    output['result'] = "no formatter"
    output['version'] = None
    return


def format_default(output, _):
    output['result'] = "no formatter"
    output['version'] = "unknown"
    return

probe_formatter = {
    # antivirus
    'ClamAV': format_av,
    'ComodoCAVL': format_av,
    'EsetNod32': format_av,
    'FProt': format_av,
    'Kaspersky': format_av,
    'McAfeeVSCL': format_av,
    'Sophos': format_av,
    'Symantec': format_av,
    # database
    'Nsrl': format_nsrl,
    # information
    'StaticAnalyzer': format_static,
    # web
    'VirusTotal': format_vt,
    }


def format_result(probe, result):
    formatter = probe_formatter.get(probe, format_default)
    res = {}
    formatter(res, result)
    return res
