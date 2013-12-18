from fields import SingleNodeManager, NodeDictManager
from fields import UUIDMapper, NameMapper, AbsFilePathMapper
from fields import Field, DictField, IntegerField

class UnsignedLongField(IntegerField):

    def __init__(self, xpath, *args, **kwargs):
        super(UnsignedLongField, self).__init__(xpath, *args, **kwargs)

class ShortIntegerField(IntegerField):

    def __init__(self, xpath, *args, **kwargs):
        super(ShortIntegerField, self).__init__(xpath, *args, **kwargs)

class UnixPermissionField(IntegerField):

    _pattern = "[0-7]{3}"

    def __init__(self, xpath, *args, **kwargs):
        super(UnixPermissionField, self).__init__(xpath, UnixPermissionField._pattern, *args, **kwargs)

class UUIDField(Field):

    def __init__(self, xpath, normalize=False, *args, **kwargs):
        super(UUIDField, self).__init__(xpath,
                manager = SingleNodeManager(),
                mapper = UUIDMapper(normalize=normalize), *args, **kwargs)

class NameField(Field):

    def __init__(self, xpath, normalize=False, *args, **kwargs):
        super(NameField, self).__init__(xpath,
                manager = SingleNodeManager(),
                mapper = NameMapper(normalize=normalize), *args, **kwargs)

class AbsFilePathField(Field):

    def __init__(self, xpath, normalize=False, *args, **kwargs):
        super(AbsFilePathField, self).__init__(xpath,
                manager = SingleNodeManager(),
                mapper = AbsFilePathMapper(normalize=normalize), *args, **kwargs)

class FilePathField(Field):

    def __init__(self, xpath, normalize=False, *args, **kwargs):
        super(FilePathField, self).__init__(xpath,
                manager = SingleNodeManager(),
                mapper = FilePathMapper(normalize=normalize), *args, **kwargs)

class StringDictField(DictField):

    def __init__(self, xpath, key, normalize=False, choices=None, *args, **kwargs):
        self.choices = choices
        super(StringDictField, self).__init__(xpath,
                manager = NodeDictManager(key),
                mapper = StringMapper(normalize=normalize, choices=choices), *args, **kwargs)

class NodeDictField(DictField):

    def __init__(self, xpath, key, node_class, *args, **kwargs):
        self.key = key
        super(NodeDictField, self).__init__(xpath,
                manager = NodeDictManager(key),
                mapper = node_class, *args, **kwargs)
