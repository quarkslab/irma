import logging, os, tempfile
from probe.modules.static.analyzer import StaticAnalyzer

version = None

def get_version():
    return StaticAnalyzer.version

def get_scan_result(data):
    (fd, filename) = tempfile.mkstemp()
    tmpfile = open(filename, "wb")
    tmpfile.write(data)
    tmpfile.close()
    os.close(fd)
    result = StaticAnalyzer.analyze(filename)
    os.unlink(filename)
    return result

def scan(sfile):
    res = {}
    if not version:
        get_version()
    res['version'] = version
    res['result'] = get_scan_result(sfile.data)
    return res
