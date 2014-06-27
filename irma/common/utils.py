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
    launched = 10
    cancelling = 20
    cancelled = 21
    processed = 30
    finished = 50
    flushed = 100
    error = 200
    error_probe_missing = 201
    label = {created: "created",
             launched: "launched",
             cancelling: "cancelling",
             cancelled: "cancelled",
             processed: "processed",
             finished: "finished",
             flushed: "flushed",
             error:"error",
             error_probe_missing:"error probe missing"
             }


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
    lock_timeout = 60   # in seconds (delta between timestamps)


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
