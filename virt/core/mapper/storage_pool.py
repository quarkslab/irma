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

import logging
import xmltodict

from collections import OrderedDict

from virt.core.exceptions import StoragePoolError

log = logging.getLogger(__name__)


# TODO: create our own mapper based on xpath and the code available at
# http://stackoverflow.com/questions/5661968/
class StoragePool(OrderedDict):

    @staticmethod
    def parse(xml):
        # TODO: this is a temporary wrapper, to be improved in the future
        try:
            xml_dict = xmltodict.parse(xml)
            return StoragePool(xml_dict["pool"])
        # error when fetching values
        except KeyError as e:
            log.exception(e)
            raise StoragePoolError(e)
        # error with xmltodict
        except Exception as e:
            log.exception(e)
            raise StoragePoolError(e)

    def unparse(self, pretty=False):
        try:
            buffer = xmltodict.unparse({'pool': self})
            if pretty:
                try:
                    import xml.dom.minidom
                    nodes = xml.dom.minidom.parseString(buffer)
                    buffer = nodes.toprettyxml()
                except:
                    pass
            return buffer
        # error with xmltodict
        except Exception as e:
            log.exception(e)
            raise StoragePoolError(e)
