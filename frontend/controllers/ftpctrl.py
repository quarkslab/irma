import os
import config.parser as config
from lib.irma.ftp.handler import FtpTls
from lib.irma.common.exceptions import IrmaFileSystemError, \
    IrmaFtpError


def upload_scan(scanid, file_path_list):
    ftp_config = config.frontend_config['ftp_brain']
    host = ftp_config.host
    port = ftp_config.port
    user = ftp_config.username
    pwd = ftp_config.password
    with FtpTls(host, port, user, pwd) as ftps:
        ftps.mkdir(scanid)
        for file_path in file_path_list:
            print "Uploading file {0}".format(file_path)
            if not os.path.exists(file_path):
                raise IrmaFileSystemError("File does not exist")
            # our ftp handler store file under its sha256 name
            hashname = ftps.upload_file(scanid, file_path)
            # and file are stored under their sha256 value
            sha256 = os.path.basename(file_path)
            if hashname != sha256:
                reason = "Ftp Error: integrity failure while uploading \
                file {0} for scanid {1}".format(file_path, scanid)
                raise IrmaFtpError(reason)
    return