import re
from subprocess import Popen, PIPE

version = ""
regex = re.compile(r'([^\s]+) FOUND')

def get_version():
    global version
    p = Popen(["clamdscan", "--version"], stdout=PIPE)
    res, err = p.communicate()
    if p.returncode == 0:
        version = res.strip()
    else:
        version = "unknown"
    return

def get_scan_result(data):
    p = Popen(["clamdscan", "--no-summary", "-"], stdout=PIPE, stdin=PIPE)
    res, err = p.communicate(input=data)
    retcode = p.returncode
    if retcode == 1:
        # remove useless information "stdin :"
        m = regex.search(res)
        if m:
            return m.group(1)
        else:
            return res
    elif retcode == 0:
        return "clean"
    else:
        return "error"

def scan(sfile):
    res = {}
    if version == "":
        get_version()
    res['version'] = version
    res['result'] = get_scan_result(sfile.data)
    return res
