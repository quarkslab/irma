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

from irma.common.base.exceptions import IrmaValueError
from irma.common.utils.utils import UUID


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

    @staticmethod
    def code_to_label(code):
        return IrmaScanStatus.label.get(code, "Unknown status code")


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
    tools = "tools"
    from_label = {
        "unknown": unknown,
        "antivirus": antivirus,
        "database": database,
        "external": external,
        "metadata": metadata,
        "tools": tools,
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

    def add_file(self, fileid, probelist, mimetype):
        self.request[fileid] = dict()
        self.request[fileid]['probe_list'] = probelist
        self.request[fileid]['mimetype'] = mimetype

    def del_file(self, fileid):
        if fileid in self.request.keys():
            self.request.pop(fileid)
        return

    def get_probelist(self, fileid):
        return self.request[fileid]['probe_list']

    def set_probelist(self, fileid, value):
        self.request[fileid]['probe_list'] = value

    def get_mimetype(self, fileid):
        return self.request[fileid]['mimetype']

    def to_dict(self):
        return self.request

    def files(self):
        return self.request.keys()


# =====================
#  Irma Celery options
# =====================

def common_celery_options(app, app_name, concurrency, soft_time_limit,
                          time_limit):
    options = list()

    # app path
    options.append('--app={}'.format(app))

    # logging level
    options.append('--loglevel=info')

    # do not subscribe to other workers events.
    options.append('--without-gossip')

    # do not synchronize with other workers at startup
    options.append('--without-mingle')

    # do not send event heartbeats
    options.append('--without-heartbeat')

    # concurrency
    if concurrency != 0:
        options.append('--concurrency={}'.format(concurrency))

    # soft time limit
    options.append('--soft-time-limit={}'.format(soft_time_limit))

    # hard time limit
    options.append('--time-limit={}'.format(time_limit))

    # worker unique id
    options.append('--hostname={}-{}'.format(app_name, UUID.generate()))

    return options
