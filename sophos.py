import tempfile
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
    res, err = p.communicate()
    if p.returncode == 0:
        version = "\n".join(res.splitlines()[11:])
    else:
        version = "unknown"
    return

def get_scan_result(data):
    (fd, filename) = tempfile.mkstemp()
    tmpfile = open(filename, "wb")
    tmpfile.write(data)
    tmpfile.close()
    os.close(fd)
    p = Popen(["sav32cli.exe", "-ss", "-nc", "-nb", filename], stdout=PIPE)
    res, err = p.communicate()
    retcode = p.returncode
    os.unlink(filename)
    return resultfromoutput(retcode, res)


def scan(sfile):
    res = {}
    if not version:
        get_version()
    res['version'] = version
    res['result'] = get_scan_result(sfile.data)
    return res
