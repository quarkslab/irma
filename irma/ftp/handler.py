import logging, hashlib
from irma.common.exceptions import IrmaFtpError
from ftplib import FTP_TLS

log = logging.getLogger(__name__)

class FtpTls(object):
    """Internal database.

    This class handles the conection with ftp server over tls
    functions for interacting with it.
    """
    ##########################################################################
    # hash function for integrity
    # each uploaded file is renamed after its digest value
    # and checked at retrieval
    ##########################################################################
    hashfunc = hashlib.sha256

    ##########################################################################
    # Constructor and Destructor stuff
    ##########################################################################
    def __init__(self, host, port, user, passwd):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._conn = None
        self._connect()

    def __del__(self):
        if self._conn:
            self._disconnect()

    def __enter__(self):
        return self


    ##########################################################################
    # Private methods
    ##########################################################################

    def _connect(self):
        if self._conn:
            logging.warn("Already connected to ftp server")
        try:
            self._conn = FTP_TLS(self._host, self._user, self._passwd)
            # Explicitely ask for secure data channel
            self._conn.prot_p()
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def _disconnect(self):
        if not self._conn:
            return
        try:
            self._conn.close()
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def _hash(self, filename):
        try:
            with open(filename, "rb") as f:
                data = f.read()
            return self.hashfunc(data).hexdigest()
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def _check_hash(self, digest, filename):
        try:
            with open(filename, "rb") as f:
                if self.hashfunc(f.read()).hexdigest != digest:
                    raise IrmaFtpError("Integrity check file failed")
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    ##########################################################################
    # Public methods
    ##########################################################################
    def mkdir(self, path):
        try:
            self._conn.mkd(path)
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))
        return

    def list(self, path):
        """ list remote directory <path>"""
        try:
            return self._conn.nlst(path)
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def upload(self, path, filename):
        """ Upload <data> to remote <filename> into directory <path>"""
        try:
            dstname = self._hash(filename)
            with open(filename, "rb") as f:
                self._conn.storbinary("STOR {0}/{1}".format(path, dstname), f)
            return dstname
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def download(self, path, remotename, dstname):
        """ Download <data> to remote <filename> into directory <path>"""
        try:
            with open(dstname, 'wb') as f:
                self._conn.retrbinary("RETR {0}/{1}".format(path, remotename), lambda data: f.write(data))
            # as remotename is the digest value of the file
            self._check_hash(remotename, dstname)
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def delete(self, path, filename):
        """ Delete <filename> into directory <path>"""
        try:
            self._conn.delete("{0}/{1}".format(path, filename))
        except Exception as e:
            raise IrmaFtpError("{0}".format(e))

    def deletepath(self, path, deleteParent=False):
        # recursively delete all subdirs and files
        try:
            for f in self.list(path):
                if self.is_file(path, f):
                    self.delete(path, f)
                else:
                    self.deletepath("{0}/{1}".format(path, f), deleteParent=True)
            if deleteParent:
                self._conn.rmd(path)
        except Exception as e:
            raise IrmaFtpError("{0} [{1}]".format(e, path))

    def is_file(self, path, filename):
        try:
            pathfilename = "{0}/{1}".format(path, filename)
            current = self._conn.pwd()
            self._conn.cwd(pathfilename)
            self._conn.cwd(current)
            return False
        except:
            return True
        raise IrmaFtpError("Unable to test file {0}/{1}".format(path, filename))
