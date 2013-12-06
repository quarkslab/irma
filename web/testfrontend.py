import os, glob
import client
import time
import requests
import json
import signal
import sys

global scanid
def signal_handler(signal, frame):
   if scanid:
      print 'Cancelling scan'
      resp = requests.get(url='http://192.168.130.1:8080/scan/cancel/'+scanid)
      print resp.content
   else:
      print "No scan to cancel"
   sys.exit(0)
   return


signal.signal(signal.SIGINT, signal_handler)

path = "/home/alex/tmp/samples/samples/"
samples = []
for infile in glob.glob( os.path.join(path, "*.*") ):
   samples.append(infile)

start = time.time()
postfiles = dict(map(lambda t: (t,open(t,'rb')), samples[200:300]))
resp = requests.post('http://192.168.130.1:8080/scan', files=postfiles)
data = json.loads(resp.content)
print data
scanid = data['scanid']

scan_finished = False
while not scan_finished:
   resp = requests.get(url='http://192.168.130.1:8080/scan/progress/'+scanid)
   data = json.loads(resp.content)
   if data['result'] == "in progress":
      finished = data['finished']
      successful = data['successful']
      total = data['total']
      print "%d jobs finished (%d%%) / %d successful (%d%%)"%(finished, finished*100/total, successful, successful*100/finished)
      if finished == total:
         scan_finished = True
   time.sleep(1)

resp = requests.get(url='http://192.168.130.1:8080/scan/results/'+scanid)
data = json.loads(resp.content)
files = data['result']
for f in files:
   print "%s"%f
   for av in data['result'][f]:
      print "\t%s%s"%(av.ljust(12),data['result'][f][av]['result'].strip())
