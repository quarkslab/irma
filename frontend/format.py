


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
        if 'name' in result and 'version' in data:
            output['version'] = "{name} {version}".format(name=data['name'], version=data['version'])
        elif 'name' in data:
            output['version'] = data['name']
    else:
        output['result'] = "Error"
    return

def format_vt(output, result):
    if 'data' in result:
        data = result['data'].values()[0]
        if type(data) is int:
            output['result'] = "error {0}".format(data)
        if 'response_code' in data and data['response_code'] == 0:
            output['result'] = "file never scanned"
        if 'scans' in data:
            scan = data['scans']
            av_res = []
            for av in ['ClamAV', 'Kaspersky', 'Symantec', 'McAfee', 'Sophos']:
                if av in scan:
                    av_res.append("{0}:{1}".format(av, scan[av]['result']))
            output['result'] = " - ".join(av_res)
        if 'scan_date' in data:
            output['version'] = data['scan_date']
    else:
        output['result'] = "Error"
    return

def format_static(output, result):
    if 'data' in result:
        data = result['data'].values()[0]
        if type(data) == dict:
            res = []
            for (k, v) in data.items():
                if v is None:
                    res.append("{0}:none".format(k))
                elif type(v) == list:
                    res.append("{0}:{1}".format(k, len(v)))
                elif type(v) == int or type(v) == str:
                    res.append("{0}:{1}".format(k, v))
            output['result'] = " / ".join(res)
        else:
            output['result'] = "no results"
    else:
        output['result'] = "Error"
    return

def format_nsrl(output, result):
    output['result'] = "no formatter"
    output['version'] = "unknown"
    return

def format_default(output, result):
    output['result'] = "no formatter"
    output['version'] = "unknown"
    return

def sanitize_dict(d):
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = sanitize_dict(v)
        new[k.replace('.', '_')] = v
    return new

probe_formatter = {
                   'Kaspersky':format_av,
                   'Sophos':format_av,
                   'McAfeeVSCL':format_av,
                   'ClamAV':format_av,
                   'Symantec':format_av,
                   'VirusTotal':format_vt,
                   'StaticAnalyzer':format_static,
                   'Nsrl':format_nsrl
                   }

def format_result(probe, raw_result):
    res = {}
    res['probe_res'] = sanitize_dict(raw_result)
    formatter = probe_formatter.get(probe, format_default)
    formatter(res, raw_result)
    return res

