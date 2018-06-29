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


class IrmaDependencyError(Exception):
    """Error caused by a missing dependency."""
    pass


class IrmaAdminError(Exception):
    """Error in admin part."""
    pass


class IrmaDatabaseError(Exception):
    """Error on a database manager."""
    pass


class IrmaCoreError(Exception):
    """Error in core parts (Db, Ftp, Celery..)"""
    pass


class IrmaDatabaseResultNotFound(IrmaDatabaseError):
    """A database result was required but none was found."""
    pass


class IrmaFileSystemError(IrmaDatabaseError):
    """Nothing corresponding to the request has been found in the database."""
    pass


class IrmaConfigurationError(IrmaCoreError):
    """Error wrong configuration."""
    pass


class IrmaFtpError(IrmaCoreError):
    """Error on ftp manager."""
    pass


class IrmaFTPSError(IrmaFtpError):
    """Error on ftp/tls manager."""
    pass


class IrmaSFTPError(IrmaFtpError):
    """Error on sftp manager."""
    pass


class IrmaSFTPv2Error(IrmaFtpError):
    """Error on sftp manager."""
    pass


class IrmaTaskError(IrmaCoreError):
    """Error while processing celery tasks."""
    pass


class IrmaValueError(Exception):
    """Error for the parameters passed to the functions"""
    pass
