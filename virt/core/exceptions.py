class ConnectionManagerError(Exception):
    """Error on establishing a connection to a remote virtual machine manager"""
    pass

class DomainManagerError(Exception):
    """Error on managing a domain"""
    pass
