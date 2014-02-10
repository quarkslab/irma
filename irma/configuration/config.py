from lib.irma.common.objects import AttributeDictionary
from ConfigParser import RawConfigParser

class Configuration(AttributeDictionary):
    pass

class ConfigurationSection(Configuration):
    pass

class TemplatedParam(object):
    func = None

    def __init__(self, default=None):
        self.default = default

class TpInteger(TemplatedParam):
    func = RawConfigParser.getint

class TpBoolean(TemplatedParam):
    func = RawConfigParser.getboolean

class TpString(TemplatedParam):
    func = RawConfigParser.get
