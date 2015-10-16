#
# Copyright (c) 2013-2014 QuarksLab.
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

from .exceptions import IrmaValueError


# ==========================
#  Tasks response formatter
# ==========================

class IrmaTaskReturn:
    @staticmethod
    def success(msg):
        return (IrmaReturnCode.success, msg)

    @staticmethod
    def warning(msg):
        return (IrmaReturnCode.warning, msg)

    @staticmethod
    def error(msg):
        return (IrmaReturnCode.error, msg)


# =============================
#  Frontend response formatter
# =============================

class IrmaFrontendReturn:
    @staticmethod
    def response(code, msg, **kwargs):
        ret = {'code': code, 'msg': msg}
        ret.update(kwargs)
        return ret

    @staticmethod
    def success(msg="success", **kwargs):
        return IrmaFrontendReturn.response(IrmaReturnCode.success,
                                           msg,
                                           **kwargs)

    @staticmethod
    def warning(msg, **kwargs):
        return IrmaFrontendReturn.response(IrmaReturnCode.warning,
                                           msg,
                                           **kwargs)

    @staticmethod
    def error(msg, **kwargs):
        return IrmaFrontendReturn.response(IrmaReturnCode.error,
                                           msg,
                                           **kwargs)


# =============
#  Return code
# =============

class IrmaReturnCode:
    success = 0
    warning = 1
    error = -1
    label = {success: "success",
             warning: "warning",
             error: "error"}


# ==============================
#  Scan status (Brain/Frontend)
# ==============================

class IrmaScanStatus:
    empty = 0
    ready = 10
    uploaded = 20
    launched = 30
    processed = 40
    finished = 50
    flushed = 60
    # cancel
    cancelling = 100
    cancelled = 110
    # errors
    error = 1000
    # Probes 101x
    error_probe_missing = 1010
    error_probe_na = 1011
    # FTP 102x
    error_ftp_upload = 1020

    label = {empty: "empty",
             ready: "ready",
             uploaded: "uploaded",
             launched: "launched",
             processed: "processed",
             finished: "finished",
             cancelling: "cancelling",
             cancelled: "cancelled",
             flushed: "flushed",
             error: "error",
             error_probe_missing: "probelist missing",
             error_probe_na: "probe(s) not available",
             error_ftp_upload: "ftp upload error"
             }

    @staticmethod
    def is_error(code):
        return code >= IrmaScanStatus.error

    @staticmethod
    def filter_status(status, status_min=None, status_max=None):
        if status not in IrmaScanStatus.label.keys():
            raise IrmaValueError("Unknown scan status {0}".format(status))
        status_str = IrmaScanStatus.label[status]
        if status_min is not None and status < status_min:
            raise IrmaValueError("Wrong scan status [{0}]".format(status_str))
        if status_max is not None and status > status_max:
            raise IrmaValueError("Wrong scan status [{0}]".format(status_str))
        return


# ==========================================================
#  Lock values for NoSQLDatabaseObjects (internal use only)
# ==========================================================

class IrmaLock:
    free = 0
    locked = 5
    label = {
        free: 'free',
        locked: 'locked'
    }
    lock_timeout = 60  # in seconds (delta between timestamps)


# =========================================================================
#  Lock values for NoSQLDatabaseObjects (FOR THE CALL TO THE CONSTRUCTORS)
# =========================================================================

class IrmaLockMode:
    read = 'r'
    write = 'w'
    label = {
        read: 'read',
        write: 'write'
    }


# ======================
#  Irma Probe Type Enum
# ======================

class IrmaProbeType:
    unknown = "unknown"
    antivirus = "antivirus"
    database = "database"
    external = "external"
    metadata = "metadata"
    from_label = {
        "unknown": unknown,
        "antivirus": antivirus,
        "database": database,
        "external": external,
        "metadata": metadata
        }

    @staticmethod
    def normalize(probe_type):
        if probe_type not in IrmaProbeType.from_label.keys():
            return IrmaProbeType.unknown
        else:
            return IrmaProbeType.from_label[probe_type]

# ==================
#  Irma ScanRequest
# ==================


class IrmaScanRequest(object):

    def __init__(self, dict_object=None):
        if dict_object is None:
            self.request = dict()
        else:
            self.request = dict_object

    @property
    def nb_files(self):
        return len(self.request.keys())

    def add_file(self, filehash, probelist, mimetype):
        self.request[filehash] = dict()
        self.request[filehash]['probe_list'] = probelist
        self.request[filehash]['mimetype'] = mimetype

    def del_file(self, filehash):
        if filehash in self.request.keys():
            self.request.pop(filehash)
        return

    def get_probelist(self, filehash):
        return self.request[filehash]['probe_list']

    def set_probelist(self, filehash, value):
        self.request[filehash]['probe_list'] = value

    def get_mimetype(self, filehash):
        return self.request[filehash]['mimetype']

    def to_dict(self):
        return self.request

    def filehashes(self):
        return self.request.keys()
