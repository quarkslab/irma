import logging, unittest, os

from lib.irma.configuration.config import ConfigurationSection
from lib.irma.configuration.ini import IniConfiguration


##############################################################################
# Logging options
##############################################################################
def enable_logging(level=logging.INFO, handler=None, formatter=None):
    log = logging.getLogger()
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    if handler is None:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)


##############################################################################
# Test Cases
##############################################################################
class CheckIniConfiguration(unittest.TestCase):

    def test_ini_config_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = IniConfiguration("{0}/test.cfg".format(directory))
        self.assertEquals(config["foo"].bar, "foobar")
        self.assertEquals(config["foo bar"].foo, "foo")
        self.assertEquals(config["foo bar"].bar, "bar")

    def test_ini_config_types(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = IniConfiguration("{0}/test.cfg".format(directory))
        self.assertEquals(isinstance(config, IniConfiguration), True)
        self.assertEquals(isinstance(config["foo bar"], ConfigurationSection), True)
        self.assertEquals(isinstance(config["foo bar"].bar, str), True)

if __name__ == '__main__':
    enable_logging()
    unittest.main()
