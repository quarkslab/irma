import os
import re
from subprocess import Popen, PIPE

version = None
regex = re.compile(r'>>> Virus \'(.*)\' found.*')

def resultfromoutput(code, stdout):
    m = regex.search(stdout)
    if m:
        return m.group(1)
    else:
        return "clean"

def get_version():
    global version
    p = Popen(["sav32cli.exe", "-v"], stdout=PIPE)
    out, _ = p.communicate()
    # win fr charset to utf8
    res = out.decode("cp1252")
    if p.returncode == 0:
        version = "\n".join(res.splitlines()[11:])
    else:
        version = "unknown"
    return

def get_scan_result(filename):
    p = Popen(["sav32cli.exe", "-ss", "-nc", "-nb", filename], stdout=PIPE)
    out, _ = p.communicate()
    # win fr charset to utf8
    res = out.decode("cp1252")
    retcode = p.returncode
    return resultfromoutput(retcode, res)


def scan(filename):
    res = {}
    if not version:
        get_version()
    res['version'] = version
    res['result'] = get_scan_result(filename)
    return res
