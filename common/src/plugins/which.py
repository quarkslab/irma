#
# Copyright (c) 2013 Preet Kukreti
#
# Excerpt of code taken at
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python

import os
import sys
import stat
import tempfile


def is_case_sensitive_filesystem():
    tmphandle, tmppath = tempfile.mkstemp()
    is_insensitive = os.path.exists(tmppath.upper())
    os.close(tmphandle)
    os.remove(tmppath)
    return not is_insensitive


_IS_CASE_SENSITIVE_FILESYSTEM = is_case_sensitive_filesystem()


def which(program, case_sensitive=_IS_CASE_SENSITIVE_FILESYSTEM):
    """
        Simulates unix `which` command.

        Returns absolute path if program found
    """

    def is_exe(fpath):
        """
            Return true if fpath is a file we have access to
            that is executable
        """
        accessmode = os.F_OK | os.X_OK
        if os.path.exists(fpath) and os.access(fpath, accessmode) and \
           not os.path.isdir(fpath):
            filemode = os.stat(fpath).st_mode
            ret = bool(filemode & stat.S_IXUSR or
                       filemode & stat.S_IXGRP or
                       filemode & stat.S_IXOTH)
            return ret

    def list_file_exts(directory, search_filename=None, ignore_case=True):
        """
            Return list of (filename, extension) tuples which match
            the search_filename
        """
        if ignore_case:
            search_filename = search_filename.lower()
        for root, dirs, files in os.walk(path):
            for f in files:
                filename, extension = os.path.splitext(f)
                if ignore_case:
                    filename = filename.lower()
                if not search_filename or filename == search_filename:
                    yield (filename, extension)
            break

    fpath, fname = os.path.split(program)

    # is a path: try direct program path
    if fpath:
        if is_exe(program):
            return program
    elif "win" in sys.platform:
        # isnt a path: try fname in current directory on windows
        if is_exe(fname):
            return program

    paths = os.environ.get("PATH", "").split(os.pathsep)
    paths = [path.strip('"') for path in paths]
    exe_exts = [ext for ext in os.environ.get("PATHEXT", "").split(os.pathsep)]
    if not case_sensitive:
        exe_exts = list(map(str.lower, exe_exts))

    # try append program path per directory
    for path in paths:
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
            return exe_file

    # try with known executable extensions per program path per directory
    for path in paths:
        filepath = os.path.join(path, program)
        for extension in exe_exts:
            exe_file = filepath + extension
            if is_exe(exe_file):
                return exe_file

    # try search program name with "soft" extension search
    if len(os.path.splitext(fname)[1]) == 0:
        for path in paths:
            file_exts = list_file_exts(path, fname, not case_sensitive)
            for file_ext in file_exts:
                filename = "".join(file_ext)
                exe_file = os.path.join(path, filename)
                if is_exe(exe_file):
                    return exe_file

    return None
