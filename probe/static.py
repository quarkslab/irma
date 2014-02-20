import logging, os, tempfile
from probe.modules.static.analyzer import StaticAnalyzer

version = None

def get_version():
    return StaticAnalyzer.version

def get_scan_result(filename):
    result = StaticAnalyzer.analyze(filename)
    os.unlink(filename)
    return result

def scan(filename):
    res = {}
    if not version:
        get_version()
    res['version'] = version
    res['result'] = get_scan_result(filename)
    return res
