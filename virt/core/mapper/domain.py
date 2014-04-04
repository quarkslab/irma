import logging
import xmltodict
from collections import OrderedDict

from virt.core.exceptions import DomainError

log = logging.getLogger(__name__)


# TODO: create our own mapper based on xpath and the code available at
# http://stackoverflow.com/questions/5661968/
class Domain(OrderedDict):

    @staticmethod
    def parse(xml):
        # TODO: this is a temporary wrapper, to be improved in the future
        try:
            xml_dict = xmltodict.parse(xml)
            return Domain(xml_dict['domain'])
        # error when fetching values
        except KeyError as e:
            log.exception(e)
            raise DomainError(e)
        # error with xmltodict
        except Exception as e:
            log.exception(e)
            raise DomainError(e)

    def unparse(self, pretty=False):
        try:
            buffer = xmltodict.unparse({'domain': self})
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
            raise DomainError(e)
