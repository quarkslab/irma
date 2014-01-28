import logging, xmltodict
from collections import OrderedDict

from lib.common import compat
from lib.virt.core.exceptions import StoragePoolError

log = logging.getLogger(__name__)

# TODO: create our own mapper based on xpath and the code available at
# http://stackoverflow.com/questions/5661968/how-to-populate-xml-file-using-xpath-in-python
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
