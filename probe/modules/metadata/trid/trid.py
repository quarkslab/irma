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

import re
import os
import sys
import locale
import logging

from subprocess import Popen, PIPE

log = logging.getLogger(__name__)


class TrID(object):

    @staticmethod
    def build_cmd(cmd, *args):
        cmd = [cmd]
        for param in args:
            if isinstance(param, (tuple, list)):
                cmd.extend(param)
            else:
                cmd.append(param)
        return " ".join(cmd)

    @staticmethod
    def run_cmd(cmd):
        # remove whitespace with re.sub, then split()
        re.sub(r'\s+', ' ', cmd)
        cmdarray = cmd.split()
        # execute command with popen, clean up outputs
        pd = Popen(cmdarray, stdout=PIPE, stderr=PIPE)
        raw_stdout, stderr = map(lambda x: x.strip() if x.strip() else None,
                                 pd.communicate())
        retcode = pd.returncode
        if raw_stdout is not None and sys.platform.startswith('win'):
            # get local encoding
            local_encoding = sys.__stdout__.encoding
            if local_encoding is None:
                local_encoding = locale.getpreferredencoding()
            # decode local encoding of stdout
            stdout = raw_stdout.decode(local_encoding)
        else:
            stdout = raw_stdout
        # return tuple (retcode, out, err)
        return (retcode, stdout, stderr)

    @staticmethod
    def get_trid_path():
        trid = os.path.join('/opt/trid/', 'trid')
        return trid if os.path.exists(trid) else None

    def check_analysis_results(self, paths, results):
        retcode, stdout, stderr = results
        # check stdout
        if stdout:
            results = []
            # iterate through lines
            for line in stdout.splitlines()[4:]:
                # find info with pattern matching
                match = re.match(b'\s*(?P<ratio>\d*[.]\d*)[%]\s+'  # percentage
                                 b'[(](?P<ext>[.]\w*)[)]\s+'  # extension
                                 b'(?P<desc>.*)$',  # remaining string
                                 line)
                # create entries to be appended to results
                if match:
                    entry = {
                        'ratio': match.group('ratio'),
                        'ext':   match.group('ext'),
                        'desc':  match.group('desc'),
                    }
                    results.append(entry)
        # uniformize retcode (1 is success)
        retcode = 1 if results else 0
        if not results:
            results = None
        return retcode, results

    def analyze(self, paths):
        cmd = self.build_cmd(self.get_trid_path(), paths)
        results = self.run_cmd(cmd)
        return self.check_analysis_results(paths, results)
