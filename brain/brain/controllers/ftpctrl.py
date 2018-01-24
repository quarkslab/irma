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


def flush(ftpuser, filename_list):
    IrmaFTP = config.get_ftp_class()
    conf_ftp = config.brain_config['ftp_brain']
    with IrmaFTP(conf_ftp.host,
                 conf_ftp.port,
                 conf_ftp.auth,
                 conf_ftp.key_path,
                 conf_ftp.username,
                 conf_ftp.password,
                 dst_user=ftpuser) as ftp:
        for filename in filename_list:
            ftp.delete(".", filename)
