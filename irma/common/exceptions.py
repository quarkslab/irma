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


class IrmaDependencyError(Exception):
    """Error caused by a missing dependency."""
    pass


class IrmaMachineManagerError(Exception):
    """Error on a machine manager."""
    pass


class IrmaMachineError(Exception):
    """Error on a machine."""
    pass


class IrmaAdminError(Exception):
    """Error in admin part."""
    pass


class IrmaValueError(Exception):
    """Error for the parameters passed to the functions"""
    pass


class IrmaCoreError(Exception):
    """Error in core parts (Db, Ftp, Celery..)"""
    pass


class IrmaConfigurationError(IrmaCoreError):
    """Error wrong configuration."""
    pass


class IrmaDatabaseError(IrmaCoreError):
    """Error on a database manager."""
    pass


class IrmaDatabaseResultNotFound(IrmaDatabaseError):
    """A database result was required but none was found."""
    pass


class IrmaLockError(IrmaDatabaseError):
    """Error for the locks on db content (already taken)"""
    pass


class IrmaLockModeError(IrmaDatabaseError):
    """Error for the mode of the locks (doesn't exist)"""
    pass


class IrmaFtpError(IrmaCoreError):
    """Error on ftp manager."""
    pass


class IrmaTaskError(IrmaCoreError):
    """Error while processing celery tasks."""
    pass
