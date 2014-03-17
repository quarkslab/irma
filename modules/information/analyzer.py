import logging, re, os

log = logging.getLogger(__name__)

class StaticAnalyzer(object):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, *args, **kwargs):
        global PE, Magic
        # late import to avoid to have dependencies
        from modules.information.pe import PE
        from lib.common.mimetypes import Magic

    ##########################################################################
    # public methods
    ##########################################################################

    _handlers = {
        re.compile('PE32') : lambda filename, data, kwargs: PE(filename, data, kwargs).analyze()
    }

    @classmethod
    def analyze(cls, filename=None, data=None, **kwargs):
        # check parameters
        if not filename and not data:
            return None
        if filename and data:
            log.error("either filename ({0}) or data ({1}) should be set".format(filename, data))
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
