#
# Copyright (c) 2013-2018 Quarkslab.
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
from irma.common.base.exceptions import IrmaFileSystemError, \
    IrmaFtpError
from tempfile import TemporaryFile


log = logging.getLogger(__name__)


def _get_ftp():
    IrmaFTP = config.get_ftp_class()
    ftp_config = config.frontend_config['ftp_brain']
    host = ftp_config.host
    port = ftp_config.port
    auth = ftp_config.auth
    key_path = ftp_config.key_path
    user = ftp_config.username
    pwd = ftp_config.password
    return IrmaFTP(host, port, auth, key_path, user, pwd)


def upload_file(upload_path, file_path):
    try:
        with _get_ftp() as ftp:
            log.debug("file_ext_id: %s uploading file: %s",
                      upload_path, file_path)
            if not os.path.isfile(file_path):
                reason = "File does not exist"
                log.error(reason)
                raise IrmaFileSystemError(reason)
            ftp.upload_file(upload_path, file_path)
        return
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        reason = "Ftp upload Error"
        raise IrmaFtpError(reason)


def download_file_data(filename):
    try:
        fobj = TemporaryFile()
        with _get_ftp() as ftp:
            log.debug("downloading file %s", filename)
            ftp.download_fobj(".", filename, fobj)
        return fobj
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        reason = "Ftp download Error"
        raise IrmaFtpError(reason)


def rename_file(srcname, dstname):
    try:
        with _get_ftp() as ftp:
            log.debug("file %s renaming to %s",
                      srcname, dstname)
            ftp.rename(srcname, dstname)
        return
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        reason = "Ftp upload Error"
        raise IrmaFtpError(reason)
