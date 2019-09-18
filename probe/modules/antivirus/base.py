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

import logging
import re
import os
import sys
from pathlib import Path

from subprocess import Popen, PIPE

log = logging.getLogger(__name__)


class EarlyInitializer(type):
    """ Metaclass needed to prevent the latter initialization of Antivirus
        attributes
    """
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        if kwargs.get("early_init", True):
            obj._init_attributes()
        return obj


class Antivirus(object, metaclass=EarlyInitializer):
    """ Antivirus Base Class
        Abstract class, should not be instanciated directly"""

    # List of attributes to initialize by calling the getter on the sub-class
    # cf. __getattr__
    _attributes = {
        # attr → default value
        "name": "unavailable",
        "database": [],
        "scan_args": (),
        "scan_path": None,
        "scan_patterns": [],
        "version": "unavailable",
        "virus_database_version": "unavailable",
    }

    # ===========
    #  Constants
    # ===========

    class ScanResult(object):
        CLEAN = 0
        INFECTED = 1
        ERROR = -1

    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        # scan tool variables
        self._scan_retcodes = {
            self.ScanResult.CLEAN: lambda x: x in [0],
            self.ScanResult.INFECTED: lambda x: x in [1],
            self.ScanResult.ERROR: lambda x:
                not self._scan_retcodes[self.ScanResult.CLEAN](x) and
                not self._scan_retcodes[self.ScanResult.INFECTED](x),
        }
        # scan pattern-matching
        self.scan_results = {}
        self._is_windows = sys.platform.startswith('win')

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError(attr)

        # eg. if `attr` is "name" then `getter` is self.get_name
        getter = getattr(self, "get_" + attr, None)
        if getter is not None:
            try:
                # Request the value of the attribute from the subclass
                value = getter()
            except Exception as e:
                log.error(
                    "Exception raised by AV {} while setting the attribute {}."
                    " exception: {}".format(self.name, attr, e))
                value = self._attributes[attr]
        else:
            value = self._attributes[attr]

        # `value` cannot not be defined
        setattr(self, attr, value)
        return value

    def _init_attributes(self):
        for attr in self._attributes:
            getattr(self, attr)

    # ====================
    #  Antivirus methods
    # ====================

    # TODO: enable multiple paths
    def scan(self, paths, env=None):
        if isinstance(paths, (tuple, list, set)):
            raise NotImplementedError(
                "Scanning of multiple paths at once is not supported for now")

        # Artifice for python <3.5 compatibility
        args = list(self.scan_args)
        args.append(paths)

        results = self.run_cmd(self.scan_path, *args, env=env)
        return self.check_scan_results(paths, results)

    # ==================
    #  Internal helpers
    # ==================

    def _run_and_parse(self, *args, regexp=None, group=None):
        retcode, stdout, _ = self.run_cmd(self.scan_path, *args)

        if retcode:
            raise RuntimeError(
                "Bad return code while getting {}".format(group))

        if regexp is None:
            return stdout

        matches = re.search(regexp, stdout, re.IGNORECASE)
        if group is None:
            return matches

        if matches is None:
            raise RuntimeError("Cannot read {} in stdout".format(group))
        else:
            return matches.group(group).strip()

    @staticmethod
    def _sanitize(elt):
        if isinstance(elt, str):
            return elt.strip()
        elif isinstance(elt, Path):
            return elt.absolute().as_posix()
        else:
            return elt

    @staticmethod
    def sanitize(iterable):
        return (Antivirus._sanitize(elt) for elt in iterable)

    @staticmethod
    def run_cmd(*cmd, env=None):
        """ Run a command
            :param cmd: The command to run. Either
                a string: eg. "ls -la /tmp"
                a sequence: eg. ["ls", "-la", Path("/tmp")]
                multiple arguments: "ls", "-la", Path("/tmp")
            :returns: the tuple (retcode, stdout, stderr) of the process. Both
                stdout and stderr are strings (unencoded data).
        """
        assert cmd

        if len(cmd) > 1:
            # case: multiple arguments
            cmd = list(Antivirus.sanitize(cmd))
        else:
            # Artifice for python <3.5 compatibility
            # cmd is necessarily a tuple of 1 argument
            unpckd_cmd = cmd[0]
            if isinstance(unpckd_cmd, Path):  # case: a Path
                cmd = list(Antivirus.sanitize(cmd))
            elif isinstance(unpckd_cmd, str):  # case: a string
                cmd = unpckd_cmd.split()
            else:  # last case: a sequence
                cmd = list(Antivirus.sanitize(unpckd_cmd))

        # execute command with popen, clean up outputs
        pd = Popen(cmd, stdout=PIPE, stderr=PIPE, env=env)
        stdout, stderr = (x.strip().decode() for x in pd.communicate())
        results = pd.returncode, stdout, stderr

        log.debug("Executed command line {},\n got {}".format(cmd, results))
        return results

    @classmethod
    def locate(cls, pattern, paths=None, syspath=True):
        """ Find a list of files or directories matching a pattern
            :param pattern: either a unix pattern (eg '*.txt', 'data.d?t',
                etc.) or a collection of such patterns
            :param paths: collection of paths to search in
            :param syspath: if True then also search in the system paths
                (envvar. PATH), else only search in `paths`
            :returns: a list of the matching files. Remark: might contains
                duplicates if `paths` and `pattern` match the same file in
                different ways
        """
        # Ensures that `paths` is a list whatever the collection was before
        paths = list(paths) if paths is not None else []

        if isinstance(pattern, str):
            pattern = [pattern]

        # `pattern` is a collection (list, tuple, set, etc.) of patterns
        results = []
        for p in pattern:
            assert isinstance(p, str)
            results += cls._locate(p, paths, syspath)
        return results

    @classmethod
    def locate_one(cls, pattern, paths=None, syspath=True):
        results = cls.locate(pattern, paths, syspath)
        if len(results) == 0:
            search_paths = paths or []
            if syspath:
                search_paths += cls._get_syspaths()
            raise RuntimeError(
                "Search for {} in {} does not return any result when one was"
                " required".format(pattern, search_paths))
        return results.pop()

    @classmethod
    def _locate(cls, pattern, paths, syspath):
        # Add system path to search paths
        if syspath:
            # NOTE: requires `paths` to be a list
            paths += cls._get_syspaths()
        elif not paths:
            paths = [Path('/')]

        return (f for path in paths for f in path.glob(pattern) if f.is_file())

    def identify_threat(self, filename, out):
        for pattern in self.scan_patterns:
            for match in pattern.finditer(out):
                threat_path = Path(match.group('file').strip())
                # Some threat possibilities:
                #   /absolute-dir/.../filename
                #   /absolute-dir/.../name.zip/unzip1.zip/unzip2.zip
                #   relative-dir/.../name.zip/unzip1.zip/unzip2.zip

                if filename == threat_path or filename in threat_path.parents:
                    threat = match.group('name').strip()
                    if threat:
                        return threat

    def check_scan_results(self, fpath, results):
        log.debug("scan results for {0}: {1}".format(fpath, results))
        CLEAN = self.ScanResult.CLEAN
        INFECTED = self.ScanResult.INFECTED
        ERROR = self.ScanResult.ERROR

        retcode, stdout, stderr = results
        self.scan_results = {}

        # 1/ get meaning of retcode
        if self._scan_retcodes[INFECTED](retcode):
            retcode = INFECTED
        elif self._scan_retcodes[ERROR](retcode):
            retcode = ERROR
            log.error("command line returned {}: {}".format(
                retcode, (stdout, stderr)))
        elif self._scan_retcodes[CLEAN](retcode):
            retcode = CLEAN
        else:
            raise RuntimeError(
                "unhandled return code {} in class {}: {}".format(
                    retcode, type(self).__name__, results))

        # 2/ handle the retcode
        if retcode == INFECTED:
            threat = self.identify_threat(fpath, stdout)
            if threat:
                self.scan_results[fpath] = threat
            else:
                retcode = ERROR if stderr else CLEAN
        if retcode == ERROR:
            self.scan_results[fpath] = stderr
        elif retcode == CLEAN:
            self.scan_results[fpath] = None

        return retcode


class AntivirusUnix(Antivirus):
    """ Unix Antivirus Base Class
        Abstract class, should not be instanciated directly"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def _get_syspaths(cls):
        try:
            return (Path(p) for p in os.environ['PATH'].split(os.pathsep))
        except KeyError as e:
            log.error("No environment variable PATH found while looking "
                      "for system paths. exception: {}".format(e))
            return []


class AntivirusWindows(Antivirus):
    """ Windows Antivirus Base Class
        Abstract class, should not be instanciated directly"""

    _envpaths = ['PROGRAMFILES', 'PROGRAMFILES(X86)']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def _get_syspaths(cls):
        syspaths = []
        for ep in cls._envpaths:
            try:
                syspaths.append(Path(os.environ[ep]))
            except KeyError as e:
                log.error("No environment variable {} found while looking "
                          "for system paths. exception: {}".format(ep, e))
        return syspaths
