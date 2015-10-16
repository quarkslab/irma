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

import logging
import re
import os
import sys
import glob
import locale

from subprocess import Popen, PIPE
from lib.common.hash import sha256sum

log = logging.getLogger(__name__)


class Antivirus(object):
    """Antivirus Base Class"""

    # ===========
    #  Constants
    # ===========

    class ScanResult:
        CLEAN = 0
        INFECTED = 1
        ERROR = -1

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # set default antivirus information
        self._name = None
        self._version = None
        self._database = None
        # scan tool variables
        self._scan_path = None
        self._scan_args = []
        self._scan_retcodes = {
            self.ScanResult.CLEAN: lambda x: x in [0],
            self.ScanResult.INFECTED: lambda x: x in [1],
            self.ScanResult.ERROR: lambda x:
                not self._scan_retcodes[self.ScanResult.CLEAN](x) and
                not self._scan_retcodes[self.ScanResult.INFECTED](x),
        }
        # scan pattern-matching
        self._scan_patterns = []
        self._scan_results = dict()
        self._is_windows = sys.platform.startswith('win')

    def can_handle(self, mimetype):
        # Accept all mimetypes
        return True

    # ====================
    #  Antivirus methods
    # ====================

    # TODO: enable multiple paths
    def scan_cmd(self, paths):
        cmd = self.scan_path
        args = self.scan_args
        return self.build_cmd(cmd, args, paths)

    def scan(self, paths):
        # reset result to an empty dictionary
        self._scan_results = dict()
        # check if patterns are set
        if not self.scan_patterns:
            raise ValueError("scan_patterns not defined")
        # build the command to be executed and run it
        if isinstance(paths, list):
            paths = map(os.path.abspath, paths)
        else:
            paths = os.path.abspath(paths)
        cmd = self.scan_cmd(paths)
        results = self.run_cmd(cmd)
        log.debug("Executed command line: {0}, ".format(cmd) +
                  "results {0}".format(results))
        return self.check_scan_results(paths, results)

    # ==================
    #  Internal helpers
    # ==================

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
    def locate(file, paths=None, syspath=True):
        # always add system path to search paths
        search_paths = os.environ.get('PATH', None) if syspath else None
        search_paths = search_paths.split(os.pathsep) if search_paths else []
        # append additionnal paths
        if paths:
            paths = [paths] if isinstance(paths, basestring) else list(paths)
            search_paths.extend(paths)
        # search path using glob to support meta-characters
        results = []
        search_paths = map(lambda p: os.path.join(p, file), search_paths)
        for path in search_paths:
            results.extend(glob.glob(path))
        # convert to absolute paths
        return map(os.path.abspath, results) if results else []

    def check_scan_results(self, paths, results):
        log.debug("scan results for {0}: {1}".format(paths, results))
        # create clean entries for all paths
        # TODO: add more info
        self._scan_results[paths] = None
        # unpack results and uniformize return code
        retcode, stdout, stderr = results
        if self._scan_retcodes[self.ScanResult.INFECTED](retcode):
            retcode = self.ScanResult.INFECTED
        elif self._scan_retcodes[self.ScanResult.ERROR](retcode):
            retcode = self.ScanResult.ERROR
            self._scan_results[paths] = stderr if stderr else stdout
            log.error("command line returned {0}".format(retcode) +
                      ": {0}".format((stdout, stderr)))
        elif self._scan_retcodes[self.ScanResult.CLEAN](retcode):
            retcode = self.ScanResult.CLEAN
        else:
            reason = ("unhandled return code {0} ".format(retcode) +
                      "in class {0}: ".format(type(self).__name__) +
                      "{0}".format(results))
            raise RuntimeError(reason)
        # handle infected and error error codes
        if retcode in [self.ScanResult.INFECTED, self.ScanResult.ERROR]:
            is_false_positive = True
            if stdout:
                for line in stdout.splitlines():
                    for pattern in self.scan_patterns:
                        matches = pattern.finditer(line)
                        for match in matches:
                            filename = match.group('file').lower()
                            # Handle absolute and relative paths in AV outputs
                            #
                            # Some filenames possibilities:
                            #   /absolute-dir/.../filename
                            #   /absolute-dir/.../name.zip/unzip1.zip/unzip2.zip
                            #   relative-dir/.../name.zip/unzip1.zip/unzip2.zip
                            #
                            # NOTE: as 'filename' does not correspond exactly
                            # to the filename parsed from the output, we need
                            # to inverse the conditions.
                            if paths.lower() in filename or \
                               os.path.relpath(paths.lower()) in filename:
                                name = match.group('name')
                                # NOTE: get first result, ignore others if
                                # binary is packed.
                                if name and self._scan_results[paths] is None:
                                    self._scan_results[paths] = name
                                    is_false_positive = False
                                    # NOTE: break only when a concluding result
                                    # has been found
                                    break
                        # if a match has been found, ignore other patterns
                        if not is_false_positive:
                            break
            # handle false positive
            if is_false_positive:
                if stderr or retcode in [self.ScanResult.ERROR]:
                    retcode = self.ScanResult.ERROR
                    self._scan_results[paths] = stderr if stderr else stdout
                else:
                    retcode = self.ScanResult.CLEAN
        return retcode

    # =========================================================================
    #  getters (for RO variable, for late resolution and value uniformisation)
    # =========================================================================

    @property
    def name(self):
        if not self._name:
            self._name = self.get_name()
        return self._name

    @property
    def version(self):
        if not self._version:
            self._version = self.get_version()
        return self._version

    @property
    def database(self):
        if not self._database:
            self._database = self.get_database()
            # NOTE: Expecting to have only files, thus filtering folders
            if self._database:
                self._database = filter(os.path.isfile, self._database)
        return self._database

    @property
    def scan_path(self):
        if not self._scan_path:
            self._scan_path = self.get_scan_path()
        return self._scan_path

    @property
    def scan_args(self):
        if not self._scan_args:
            self._scan_args = str(self.get_scan_args())
        return self._scan_args

    @property
    def scan_patterns(self):
        if isinstance(self._scan_patterns, (tuple, list)):
            results = self._scan_patterns
        else:
            results = list(self._scan_patterns)
        return results

    @property
    def scan_results(self):
        return self._scan_results

    # ==========================================
    #  Antivirus methods (need to be overriden)
    # ==========================================

    def get_name(self):
        """return the name of the antivirus"""
        return None

    def get_version(self):
        """return the version of the antivirus"""
        return None

    def get_database(self):
        """return list of files in the database"""
        return None

    def get_scan_path(self):
        """return the full path of the scan tool"""
        return None

    def get_scan_args(self):
        """return the scan arguments"""
        return None
