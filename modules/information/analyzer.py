import logging
import re
import os

log = logging.getLogger(__name__)


class StaticAnalyzer(object):
    # ==================================
    #  Constructor and destructor stuff
    # ==================================

    def __init__(self, *args, **kwargs):
        global PE
        global Magic
        # late import to avoid to have dependencies
        from modules.information.pe import PE
        from lib.common.mimetypes import Magic

    # ================
    #  Public methods
    # ================

    _handlers = {
        re.compile('PE32'):
        lambda filename, data, kwargs: PE(filename, data, kwargs).analyze()
    }

    @classmethod
    def analyze(cls, filename=None, data=None, **kwargs):
        # check parameters
        if not filename and not data:
            return None
        if filename and data:
            log.error("either filename ({0}) ".format(filename) +
                      "or data ({0}) should be set".format(data))
            return None
        # check if file exists
        mimetype = None
        if data:
            # guess mimetype for buffer
            mimetype = Magic.from_buffer(data)
        elif filename:
            if os.path.exists(filename):
                # guess mimetype for file
                mimetype = Magic.from_file(filename)
        # look for handle
        result = None
        if mimetype:
            handler_found = False
            for (pattern, handler) in cls._handlers.items():
                if pattern.match(mimetype):
                    result = handler(filename, data, kwargs)
                    handler_found = True
            if not handler_found:
                log.warning("{0} not yet handled".format(mimetype))
        return result
