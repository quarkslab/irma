import magic, os, logging

log = logging.getLogger(__name__)

class Magic(object):

    ##########################################################################
    # internal helpers
    ##########################################################################

    @classmethod
    def _load_database(cls, filepath=None):
        # load database
        if filepath:
            if os.path.exists(filepath):
                cls.cookie.load(filepath)
            else:
                log.warning("magic database {0} does not exist, reverting to default.".format(filepath))
                cls.cookie.load()
        else:
            cls.cookie.load()

    @classmethod
    def _set_flags(cls, mime=False, mime_encoding=False, keep_going=False):
        # setting flags
        cls.flags = magic.MAGIC_NONE
        if mime:
            cls.flags |= MAGIC_MIME
        elif mime_encoding:
            cls.flags |= MAGIC_MIME_ENCODING
        if keep_going:
            cls.flags |= MAGIC_CONTINUE
        # creating cookie
        cls.cookie = magic.open(cls.flags)       

    ##########################################################################
    # public methods
    ##########################################################################

    @classmethod
    def from_buffer(cls, buf, **kwargs):
        cls._set_flags(**kwargs)
        cls._load_database(**kwargs)
        # perform processing
        try:
            filetype = cls.cookie.buffer(data)
        except:
            try:
                filetype = magic.from_buffer(data)
            except Exception:
                filetype = None
        finally:
            try:
                cls.cookie.close()
            except:
                pass
        return filetype

    @classmethod
    def from_file(cls, filename, **kwargs):
        # reconfigure class before processing
        cls._set_flags(**kwargs)
        cls._load_database(**kwargs)
        # perform processing
        try:
            filetype = cls.cookie.file(filename)
        except:
            try:
                filetype = magic.from_file(filename)
            except:
                filetype = None
        finally:
            try:
                cls.cookie.close()
            except:
                pass
        return filetype
