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

class IrmaConfigurationError(Exception):
    """Error wrong configuration."""
    pass

class IrmaFtpError(Exception):
    """Error on ftp manager."""
    pass
