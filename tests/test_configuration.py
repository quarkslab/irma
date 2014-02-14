import logging, unittest, os
import copy
from irma.configuration.config import ConfigurationSection
from irma.configuration.ini import IniConfiguration, TemplatedConfiguration
from irma.common.exceptions import IrmaConfigurationError


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
        config = IniConfiguration("{0}/test.ini".format(directory))
        self.assertEquals(config["foo"].bar, "foobar")
        self.assertEquals(config["foo bar"].foo, "foo")
        self.assertEquals(config["foo bar"].bar, "bar")

    def test_ini_config_types(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = IniConfiguration("{0}/test.ini".format(directory))
        self.assertEquals(isinstance(config, IniConfiguration), True)
        self.assertEquals(isinstance(config["foo bar"], ConfigurationSection), True)
        self.assertEquals(isinstance(config["foo bar"].bar, str), True)


template = {
                'foo':
                     [('bar', TemplatedConfiguration.string, None)],
                'foo bar':
                    [('foo', TemplatedConfiguration.string, None),
                     ('bar', TemplatedConfiguration.string, None),
                     ('val', TemplatedConfiguration.integer, 1337)],
                'bar':
                    [('foo1', TemplatedConfiguration.integer, 42),
                     ('foo2', TemplatedConfiguration.string, "Answer")]
            }

class CheckTemplatedConfiguration(unittest.TestCase):

    def test_templated_config_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = TemplatedConfiguration("{0}/test.ini".format(directory), template)
        self.assertEquals(isinstance(config, TemplatedConfiguration), True)
        self.assertEquals(config["foo"].bar, "foobar")
        self.assertEquals(config["foo bar"].foo, "foo")
        self.assertEquals(config["foo bar"].bar, "bar")

    def test_templated_config_default_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        config = TemplatedConfiguration("{0}/test.ini".format(directory), template)
        self.assertEquals(config["foo bar"].val, 1337)
        self.assertEquals(config["bar"].foo1, 42)
        self.assertEquals(config["bar"].foo2, "Answer")

    def test_templated_config_missing_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = [('missingkey', TemplatedConfiguration.string, None)]
        with self.assertRaises(IrmaConfigurationError):
            TemplatedConfiguration("{0}/test.ini".format(directory), template1)

    def test_templated_config_section_only_default_value(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = [('missingkey', TemplatedConfiguration.string, "with_def_value")]
        config = TemplatedConfiguration("{0}/test.ini".format(directory), template1)
        self.assertEquals(isinstance(config["missingsection"], ConfigurationSection), True)
        self.assertEquals(config["missingsection"].missingkey, "with_def_value")

    def test_templated_config_value_with_space(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = [('one missing key', TemplatedConfiguration.string, "with_def_value")]
        config = TemplatedConfiguration("{0}/test.ini".format(directory), template1)
        self.assertEquals(isinstance(config["missingsection"], ConfigurationSection), True)
        self.assertEquals(config["missingsection"]["one missing key"], "with_def_value")

    def test_templated_config_wrong_template(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        template1 = copy.copy(template)
        template1['missingsection'] = (('key', TemplatedConfiguration.string, None))
        with self.assertRaises(IrmaConfigurationError):
            TemplatedConfiguration("{0}/test.ini".format(directory), template1)

if __name__ == '__main__':
    enable_logging()
    unittest.main()

