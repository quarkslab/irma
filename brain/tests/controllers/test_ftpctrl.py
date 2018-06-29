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

from unittest import TestCase
from mock import MagicMock, patch
import brain.controllers.ftpctrl as module
import config.parser as config


class TestFtpCtrl(TestCase):

    @patch("config.parser.IrmaSFTPv2")
    def test_flush(self, m_IrmaSFTPv2):
        m_ftp = MagicMock()
        m_IrmaSFTPv2().__enter__.return_value = m_ftp
        ftpuser = "ftpuser"
        m_file1 = "m_file1"
        m_file2 = "m_file2"
        files = [m_file1, m_file2]
        module.flush(ftpuser, files)
        conf_ftp = config.brain_config['ftp_brain']
        m_IrmaSFTPv2.assert_any_call(conf_ftp.host,
                                     conf_ftp.port,
                                     conf_ftp.auth,
                                     conf_ftp.key_path,
                                     conf_ftp.username,
                                     conf_ftp.password,
                                     dst_user=ftpuser)
        m_ftp.delete.assert_any_call('.', m_file1)
        m_ftp.delete.assert_any_call('.', m_file2)
