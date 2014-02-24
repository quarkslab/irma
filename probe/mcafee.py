import re
from subprocess import Popen, PIPE

version = None
regex = re.compile(r'Found the (^\n+)\n')

def resultfromoutput(code, stdout):
    m = regex.search(stdout)
    if m:
        return m.group(1) + "(%d)" % code
    else:
        return "clean (%d)" % code

def get_version():
    global version
    p = Popen(["scan.exe", "/VERSION"], stdout=PIPE)
    out, _ = p.communicate()
    # win fr charset to utf8
    res = out.decode("cp1252")
    if p.returncode == 0:
        ver_array = res.splitlines()
        version = "\n".join(ver_array[0] + ver_array[4:])
    else:
        version = "unknown"
    return

def get_scan_result(filename):
    p = Popen(["scan.exe", "/NOMEM", filename], stdout=PIPE)
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
