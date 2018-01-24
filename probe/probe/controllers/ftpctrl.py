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

import config.parser as config
import os
import logging


log = logging.getLogger(__name__)


def download_file(frontend, srcname, dstname):
    IrmaFTP = config.get_ftp_class()
    ftp_config = config.probe_config['ftp_brain']
    with IrmaFTP(ftp_config.host,
                 ftp_config.port,
                 ftp_config.auth,
                 ftp_config.key_path,
                 ftp_config.username,
                 ftp_config.password,
                 dst_user=frontend) as ftp:
        log.debug("download %s in %s frontend %s", srcname,
                  dstname, frontend)
        ftp.download_file(".", srcname, dstname)


def upload_files(frontend, path, srcname_list, parent_filename):
    IrmaFTP = config.get_ftp_class()
    uploaded_files = {}
    ftp_config = config.probe_config['ftp_brain']
    with IrmaFTP(ftp_config.host,
                 ftp_config.port,
                 ftp_config.auth,
                 ftp_config.key_path,
                 ftp_config.username,
                 ftp_config.password,
                 dst_user=frontend) as ftp:
        index = 0
        for srcname in srcname_list:
            full_path = os.path.join(path, srcname)
            if os.path.isdir(full_path):
                continue
            dstname = "{}_{}".format(parent_filename, index)
            index += 1
            log.debug("upload %s in %s", full_path, dstname)
            ftp.upload_file(dstname, full_path)
            uploaded_files[srcname] = dstname
    return uploaded_files
