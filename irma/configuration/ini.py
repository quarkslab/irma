try:
    from ConfigParser import ConfigParser
except ImportError:
    # ConfigParser module has been renamed to configparser in python 3
    from configparser import ConfigParser
from lib.irma.common.exceptions import IrmaConfigurationError
from lib.irma.configuration.config import Configuration, ConfigurationSection

class IniConfiguration(Configuration):
    """Windows ini-like configuration file parser."""

    def __init__(self, cfg_file):
        """@param cfg_file: file path of the configuration file."""
        config = ConfigParser()
        config.read(cfg_file)

        for section in config.sections():
            setattr(self, section, ConfigurationSection())
            for name in config.options(section):
                try:
                    value = config.getboolean(section, name)
                except ValueError:
                    try:
                        value = config.getint(section, name)
                    except ValueError:
                        value = config.get(section, name)
                setattr(getattr(self, section), name, value)

class TemplatedConfiguration(Configuration):
    """Windows ini-like configuration file parser with template for required keys and their types."""
    boolean = 0
    integer = 1
    string = 2

    def __init__(self, cfg_file, template):
        """
        @param cfg_file: file path of the configuration file.
        @param template: list of tuples with {section:(key_name, key_type)}
        """
        config = ConfigParser()
        config.read(cfg_file)
        for section in template.keys():
            # setattr even if section is not present in ini file
            # as it may have default value, check at value fetching
            setattr(self, section, ConfigurationSection())

            for (key_name, key_type, key_def_value) in template[section]:
                if not config.has_option(section, key_name):
                    # If key not found but a default value exists, set it
                    if key_def_value:
                        setattr(getattr(self, section), key_name, key_def_value)
                        continue
                    else:
                        raise IrmaConfigurationError("file <%s> missing section [%s] key [%s]" % (cfg_file, section, key_name,))
                try:
                    if key_type == self.boolean:
                        value = config.getboolean(section, key_name)
                    elif key_type == self.integer:
                        value = config.getint(section, key_name)
                    else:
                        value = config.get(section, key_name)
                    setattr(getattr(self, section), key_name, value)
                except ValueError:
                    raise IrmaConfigurationError("file <%s> missing section [%s] Wrong type for key [%s]" % (cfg_file, section, key_name,))
