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


class ConnectionManagerError(Exception):
    """
    Error on establishing a connection to a
    remote virtual machine manager
    """
    pass


class DomainManagerError(Exception):
    """Error on managing a domain"""
    pass


class DomainError(Exception):
    """Error on creating a domain"""
    pass


class StoragePoolManagerError(Exception):
    """Error on managing a storage pool"""
    pass


class StoragePoolError(Exception):
    """Error on creating a storage pool"""
    pass


class StorageVolumeManagerError(Exception):
    """Error on managing a storage volume"""
    pass


class StorageVolumeError(Exception):
    """Error on creating a storage volume"""
    pass
