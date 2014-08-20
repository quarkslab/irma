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
    created = 0
    uploading = 5
    launched = 10
    cancelling = 20
    cancelled = 21
    processed = 30
    finished = 50
    flushed = 100
    error = 200
    # Probes 201-209
    error_probe_missing = 201
    error_probe_na = 202
    # FTP 210-219
    error_ftp_upload = 210
    label = {created: "created",
             uploading: "uploading",
             launched: "launched",
             cancelling: "cancelling",
             cancelled: "cancelled",
             processed: "processed",
             finished: "finished",
             flushed: "flushed",
             error: "error",
             error_probe_missing: "probelist missing",
             error_probe_na: "probe(s) not available",
             error_ftp_upload: "ftp upload error"
             }

    @staticmethod
    def is_error(code):
        return code >= IrmaScanStatus.error

# ====================
#  ScanResults states
# ====================

class IrmaProbeResultsStates:
    created = 0
    running = 10
    cancelled = 20
    finished = 30
    error = 40
    label = {
        created: "created",
        running: "running",
        cancelled: "cancelled",
        finished: "finished",
        error: "error"
    }
    


# =============
#  ScanResults
# =============

class IrmaScanResults:
    notDoneYet = 0
    isMalicious = 10
    isNotMalicious = 20
    doNotKnow = 30
    label = {
        notDoneYet: "notDoneYet",
        isMalicious: "isMalicious",
        isNotMalicious: "isNotMalicious",
        doNotKnow: "doNotKnow"
    }
