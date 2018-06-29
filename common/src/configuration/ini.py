#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from configparser import ConfigParser
from irma.common.base.exceptions import IrmaConfigurationError
from irma.common.configuration.config import Configuration, \
    ConfigurationSection


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
    """
    Windows ini-like configuration file parser
    with template for required keys and their types.
    """
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

        # load configuration file
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

        # override with default values from template
        for section in template.keys():
            # setattr even if section is not present in ini file
            # as it may have default value, check at value fetching
            setattr(self, section, ConfigurationSection())
            if type(template[section]) != list:
                reason = "Malformed Template section type should be list"
                raise IrmaConfigurationError(reason)
            for (key_name, key_type, key_def_value) in template[section]:
                if not config.has_option(section, key_name):
                    # If key not found but a default value exists, set it
                    if key_def_value is not None:
                        setattr(getattr(self, section),
                                key_name,
                                key_def_value)
                        continue
                    else:
                        reason = ("file {0} ".format(cfg_file) +
                                  "missing section {0} ".format(section) +
                                  "key {0}".format(key_name))
                        raise IrmaConfigurationError(reason)
                try:
                    if key_type == self.boolean:
                        value = config.getboolean(section, key_name)
                    elif key_type == self.integer:
                        value = config.getint(section, key_name)
                    else:
                        value = config.get(section, key_name)
                    setattr(getattr(self, section), key_name, value)
                except ValueError:
                    reason = ("file {0} ".format(cfg_file) +
                              "missing section {0} ".format(section) +
                              "Wrong type for key {0}".format(key_name))
                    raise IrmaConfigurationError(reason)
