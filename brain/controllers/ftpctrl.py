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

from lib.irma.ftp.handler import FtpTls
import config.parser as config


def flush_dir(ftpuser, scanid):
    print("Flushing dir {0}".format(scanid))
    conf_ftp = config.brain_config['ftp_brain']
    with FtpTls(conf_ftp.host,
                conf_ftp.port,
                conf_ftp.username,
                conf_ftp.password) as ftps:
        ftps.deletepath("{0}/{1}".format(ftpuser, scanid), deleteParent=True)
