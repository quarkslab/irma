import logging
import tempfile
import os


# =================
#  Logging options
# =================

def enable_logging(level=logging.INFO, handler=None, formatter=None):
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] " +
                                      "%(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)
    return log


# ==========
#  Template
# ==========
class GenericAVTest():

    expected_results = {}
    antivirus_class = None
    subfolder = None

    @staticmethod
    def ready(av):
        ready = False
        if av.scan_path and av.scan_path.exists() and av.scan_path.is_file():
            ready = True
        return ready

    def setUp(self):
        # enable logging is not yet enabled
        self.log = enable_logging()
        # get absolute path
        self.abspath = os.path.abspath('./tests/samples/')
        # create antivirus handle
        self.antivirus = self.__class__.antivirus_class()
        # check if probe is ready
        self.ready = self.__class__.ready(self.antivirus)
        if not self.ready:
            self.log.warning("{0} seems not to be available, "
                             "skipping all tests ..."
                             "".format(self.antivirus.name))

    def scan_and_check(self, filename, refresult):
        code = self.antivirus.scan(filename)
        if code >= 0:
            results = self.antivirus.scan_results.items()
            for result in results:
                # transform result as the AV returns abspath
                result = os.path.basename(result[0]), result[1]
                if result[1] != refresult:
                    self.log.error("{0}: {1} / {2}"
                                   "".format(result[0], result[1], refresult))
                self.assertEqual(result[1], refresult)
        else:
            self.log.warning("error: {0}".format(self.antivirus.scan_results))

    def test_eicar_with_fileext(self):
        if not self.ready:
            return

        for file, result in self.expected_results.items():
            if isinstance(result, (list, tuple)):
                result = result[0]
            file = os.path.join(self.abspath, self.subfolder, file)
            self.scan_and_check(file, result)

    @staticmethod
    def copy_to_tmpfile(file):
        tmpname = None
        with open(file, 'rb') as rfd:
            # create temp file
            (fd, tmpname) = tempfile.mkstemp()
            os.close(fd)
            with open(tmpname, 'wb') as wfd:
                wfd.write(rfd.read())
        return tmpname

    def test_eicar(self):
        if not self.ready:
            return

        for file, result in self.expected_results.items():
            if isinstance(result, (list, tuple)):
                result = result[1]
            file = os.path.join(self.abspath, self.subfolder, file)
            tmpname = self.__class__.copy_to_tmpfile(file)
            self.scan_and_check(tmpname, result)
            if os.path.exists(tmpname):
                os.remove(tmpname)


class GenericEicar(GenericAVTest):

    subfolder = 'eicar'
