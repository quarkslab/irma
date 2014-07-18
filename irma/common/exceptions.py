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


class IrmaDatabaseError(Exception):
    """Error on a database manager."""
    pass


class IrmaDatabaseResultNotFound(Exception):
    """Nothing corresponding to the request has been found in the database."""
    pass


class IrmaFileSystemError(Exception):
    """Nothing corresponding to the request has been found in the database."""
    pass


class IrmaConfigurationError(Exception):
    """Error wrong configuration."""
    pass


class IrmaFtpError(Exception):
    """Error on ftp manager."""
    pass


class IrmaTaskError(Exception):
    """Error while processing celery tasks."""
    pass


class IrmaValueError(Exception):
    """Error for the parameters passed to the functions"""
    pass
