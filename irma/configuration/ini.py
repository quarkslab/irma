try:
    from ConfigParser import ConfigParser
except ImportError:
    # ConfigParser module has been renamed to configparser in python 3
    from configparser import ConfigParser

from lib.irma.configuration.config import Configuration, ConfigurationSection
from lib.irma.common.exceptions import IrmaConfigurationError
from lib.irma.common.objects import AttributeDictionary

class IniConfiguration(Configuration):
    """Windows ini-like configuration file parser."""

    def __init__(self, cfg_file):
        """@param cfg_file: file path of the configuration file."""
        config = ConfigParser()
        config.read(cfg_file)

        for section in config.sections():
            setattr(self, section, ConfigurationSection())
            for name, raw_value in config.items(section):
                try:
                    value = config.getboolean(section, name)
                except ValueError:
                    try:
                        value = config.getint(section, name)
                    except ValueError:
                        value = config.get(section, name)
                setattr(getattr(self, section), name, value)
