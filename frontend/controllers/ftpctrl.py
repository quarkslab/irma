#
# Copyright (c) 2013-2015 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import os
import logging
import config.parser as config
from lib.irma.ftp.handler import FtpTls
from lib.irma.common.exceptions import IrmaFileSystemError, \
    IrmaFtpError


log = logging.getLogger(__name__)


def upload_scan(scanid, file_path_list):
    try:
        ftp_config = config.frontend_config['ftp_brain']
        host = ftp_config.host
        port = ftp_config.port
        user = ftp_config.username
        pwd = ftp_config.password
        with FtpTls(host, port, user, pwd) as ftps:
            ftps.mkdir(scanid)
            for file_path in file_path_list:
                log.debug("scanid: %s uploading file %s", scanid, file_path)
                if not os.path.exists(file_path):
                    reason = "File does not exist"
                    log.error(reason)
                    raise IrmaFileSystemError(reason)
                # our ftp handler store file under its sha256 name
                hashname = ftps.upload_file(scanid, file_path)
                # and file are stored under their sha256 value
                sha256 = os.path.basename(file_path)
                if hashname != sha256:
                    reason = "Ftp Error: integrity failure while uploading \
                    file {0} for scanid {1}".format(file_path, scanid)
                    log.error(reason)
                    raise IrmaFtpError(reason)
        return
    except Exception as e:
        log.exception(e)
        reason = "Ftp upload Error"
        raise IrmaFtpError(reason)


def download_file_data(scanid, file_sha256):
    try:
        ftp_config = config.frontend_config['ftp_brain']
        host = ftp_config.host
        port = ftp_config.port
        user = ftp_config.username
        pwd = ftp_config.password

        with FtpTls(host, port, user, pwd) as ftps:
            log.debug("scanid: %s downloading file %s", scanid, file_sha256)
            file_data = ftps.download_data(scanid, file_sha256)
        return file_data
    except Exception as e:
        log.exception(e)
        reason = "Ftp upload Error"
        raise IrmaFtpError(reason)
