import tempfile
import os
from subprocess import Popen, PIPE

def scan(sfile):
    (fd, filename) = tempfile.mkstemp()
    tmpfile = open(filename, "wb")
    tmpfile.write(sfile.data)
    tmpfile.close()
    os.close(fd)
    p = Popen(["DoSCan", "/ScanFile", filename], stdout=PIPE)
    res, err = p.communicate()
    retcode = p.returncode
    os.unlink(filename)
    return "[%d] [%s]" % (retcode, res)

