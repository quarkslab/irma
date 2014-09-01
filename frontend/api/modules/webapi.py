
class WebApi(object):
    _app = None
    _mountpath = None

    def __init__(self):
        pass

    def get_app(self):
        return self._app

    def get_mount_path(self):
        return self._mountpath
