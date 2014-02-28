import json, hashlib
import urllib, urllib2

url = "https://www.virustotal.com/vtapi/v2/file/report"

def get_scan_result(hashvalue):
    parameters = {"resource": hashvalue,
                  "apikey": "-=- YOUR KEY HERE -=-"}
    data = urllib.urlencode(parameters)
    req = urllib2.Request(url, data)
    res = urllib2.urlopen(req)
    res_json = res.read()
    try:
        vtres = json.loads(res_json)
        if vtres['response_code'] != 1:
            return "retcode %d" % vtres['response_code']
        else:
            return "%d/%d positives" % (vtres['positives'], vtres['total'])
    except:
        return "Error fetching online result"

def scan(filename):
    res = {}
    with open(filename, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    res['result'] = get_scan_result(sha256)
    return res
