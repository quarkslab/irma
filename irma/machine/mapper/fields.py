import re

from lib.common.utils import UUID

from lxml import etree
from eulxml.xpath import ast, parse, serialize
from types import ListType, FloatType

from eulxml.xmlmap import fields
from eulxml.xmlmap.fields import Field
from eulxml.xmlmap.fields import NodeList
from eulxml.xmlmap.fields import StringMapper
from eulxml.xmlmap.fields import SingleNodeManager

##############################################################################
# Basic types
##############################################################################

class NodeDict(object):
    """Custom Dict-like object to handle DictFields like :class:`IntegerDictField`,
    :class:`StringDictField`, and :class:`NodeDictField`, which allows for getting,
    setting, and deleting list members.  :class:`NodeDict` should **not** be
    initialized directly, but instead should only be accessed as the return type
    from a DictField.

    Supports common list functions and operators, including the following: len();
    **in**; equal and not equal comparison to standard python Dict.  Items can
    be retrieved, set, and deleted by index, but slice indexing is not supported.
    Supports the methods that Python documentation indicates should be provided
    by Mutable sequences, with the exceptions of reverse and sort; in the
    particular case of :class:`NodeListField`, it is unclear how a list of
    :class:`~eulxml.xmlmap.XmlObject` should be sorted, or whether or not such
    a thing would be useful or meaningful for XML content.

    When a new element is appended to a :class:`~eulxml.xmlmap.fields.NodeList`,
    it will be added to the XML immediately after the last element in the list.
    In the case of an empty list, the new content will be appended at the end of
    the appropriate XML parent node.  For XML content where element order is important
    for schema validity, extra care may be required when constructing content.
    """
    def __init__(self, xpath, key, node, context, mapper, xast):
        self.xpath = xpath
        self.key = key
        self.node = node
        self.context = context
        self.mapper = mapper
        self.xast = xast

    def _key_value(self):
        # retrieve key value from xpath passed in parameter
        key = self.node.xpath(self.key, **self.context)
        if key is None:
            raise Exception("Unable to retreive key at xpath '%s'" % self.key)
        return key[0]
        return self.key

    def matches(self, key=None):
        # current matches from the xml tree
        # NOTE: retrieving from the xml every time rather than caching
        # because the xml document could change, and we want the latest data
        if not key:
            key = self._key_value()
        if isinstance(self.xpath, dict):
            xpath = self.xpath[key]
        else:
            xpath = self.xpath
        return self.node.xpath(xpath, **self.context)

    def is_empty(self):
        '''Parallel to :meth:`eulxml.xmlmap.XmlObject.is_empty`.  A
        NodeList is considered to be empty if every element in the
        list is empty.'''
        return all(n.is_empty() for n in self)

    def _retrieve_mapper(self, key=None):
        if not key:
            key = self._key_value()
        if isinstance(self.mapper, dict):
            mapper = self.mapper.get(key, None)
            if not mapper:
                raise Exception("Unable to retreive mapper for key '%s'. Defined keys: %s" % (key, self.mapper.keys()))
        else:
            mapper = self.mapper
        return mapper

    @property
    def data(self):
        # data in dict form
        key = self._key_value()
        dictionary = { key: None }
        # add data in dictionnary
        for match in self.matches():
            mapper = self._retrieve_mapper()
            dictionary[key] = mapper.to_python(match)
        return dictionary

    def __contains__(self, item):
        return item in self.data.keys()

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for item in self.matches():
            mapper = self._retrieve_mapper()
            yield mapper.to_python(item)

    def __eq__(self, other):
        # FIXME: is any other comparison possible ?
        return self.data == other

    def __ne__(self, other):
        return self.data != other

    def __getitem__(self, key):
        mapper = self._retrieve_mapper(key)
        return mapper.to_python(self.matches(key)[0])

    def __setitem__(self, key, value):
        if not self.data.has_key(key) or not len(self.matches(key)):
            if isinstance(self.xast, dict):
                xast = self.xast.get(key, None)
            else:
                xast = self.xast
            if not xast:
                raise Exception("Unable to retreive syntactic tree for node")
            match = fields._create_xml_node(xast, self.node, self.context, 0)
        else:
            match = match[0]
        
        mapper = self._retrieve_mapper(key)
        if isinstance(mapper, NodeMapper):
            # if this is a NodeListField, the value should be an xmlobject
            # replace the indexed node with the node specified
            # NOTE: lxml does not require dom-style import before append/replace
            match.getparent().replace(match, value.node)
        else: # not a NodeListField - set single-node value in xml
            # terminal (rightmost) step informs how we update the xml
            step = fields._find_terminal_step(self.xast)
            fields._set_in_xml(match, mapper.to_xml(value), self.context, step)

    def __delitem__(self, key):
        if self.matches(key):
            for match in self.matches(key):
                match.getparent().remove(match)

    def get(self, k, dft=None):
        return self.data.get(k, dft)

    def empty(self):
        return len(self.data) == 0

    def has_key(self, k):
        return self.data.has_key(k)

    def iterkeys(self):
        return (k for k in self.data)

    def keys(self):
        return [k for k in self.iterkeys()]

    def itervalues(self):
        return (self.data[k] for k in self.data.keys())

    def values(self):
        return [v for v in self.itervalues()]

    def iteritems(self):
        return ((k, self.data[k]) for k in self.data.keys())

    def items(self):
        return [(k,v) for k,v in self.iteritems()]


##############################################################################
# Managers
##############################################################################

class SingleNodeManager(fields.SingleNodeManager): pass
class NodeListManager(fields.NodeListManager): pass

class NodeDictManager(object):

    def __init__(self, key, unique=False):
        self.unique = unique
        self.key = key

    def get(self, xpath, node, context, mapper, xast):
        value = NodeDict(xpath, self.key, node, context, mapper, xast)
        return value

    def delete(self, xpath, xast, node, context, mapper):
        current_list = self.get(xpath, node, context, mapper, xast)
        for key in current_list:
            del current_list[key]

    def set(self, xpath, xast, node, context, mapper, value):
        current_list = self.get(xpath, node, context, mapper, xast)
        # for each value in the new list, set the equivalent value
        # in the NodeList
        for i in range(len(value)):
            current_list[i] = value[i]

        # remove any extra values from end of the current list
        while len(current_list) > len(value):
            current_list.pop()


##############################################################################
# Mappers
##############################################################################

class Mapper(fields.Mapper): pass
class SimpleBooleanMapper(fields.SimpleBooleanMapper): pass
class DateTimeMapper(fields.DateTimeMapper): pass
class DateMapper(fields.DateMapper): pass
class NullMapper(fields.NullMapper): pass
class NodeMapper(fields.NodeMapper): pass

class StringMapper(fields.StringMapper):

    def __init__(self, normalize=False, choices=None):
        self.choices = choices
        super(StringMapper, self).__init__(normalize)

    def to_python(self, node):
        value = super(StringMapper, self).to_python(node) 
        if value and self.choices and value not in self.choices:
            raise Exception("String field value '%s' is not in authorized values '%s'" % (value, self.choices))
        return value

    def to_xml(self, value):
        if self.choices and value not in self.choices:
            raise Exception("String field value '%s' is not in authorized values '%s'" % (value, self.choices))
        return super(StringMapper, self).to_xml(value)

def _check_int_range(range, value):
    valid = False
    # always valid if range not set
    if not range:
        valid = True
    # range checking based on a string convertible to int or a pattern to match
    elif isinstance(range, basestring):
        # try to convert it to int
        try:
            valid = _check_int_range(int(range), value)
        # if it fails range is specified using pattern matching
        except:
            pattern = re.compile(range, re.IGNORECASE)
            valid = pattern.match(str(value))
    # range checking for a int
    elif isinstance(range, int):
        if range == value:
            valid = True
    # range checking for a list
    elif isinstance(range, (list, tuple)):
        (base, limit) = range
        if value >= base and value <= limit:
            valid = True
    else:
        raise ValueError("Integer field range checking specified in %s not yet implemented" % (type(range),))
    return valid

class IntegerMapper(fields.IntegerMapper):

    def _check_range(self, value):
        valid = False
        if isinstance(self.ranges, (tuple, list)):
            for range in self.ranges:
                if _check_int_range(range, value):
                    valid = True
                    break
        else:
            valid = _check_int_range(self.ranges, value)
        return valid

    def __init__(self, ranges=None):
        self.ranges = ranges
        super(IntegerMapper, self).__init__()

    def to_python(self, node):
        # add support for ranges
        if node is None:
            return None
        try:
            # xpath functions such as count return a float and must be converted to int
            if isinstance(node, basestring) or isinstance(node, FloatType):
                value = int(node)
            else:
                value = int(self.XPATH(node))
            if not self._check_range(value):
                raise Exception("Integer field value '%s' is not in authorized ranges '%s'" % (value, self.ranges))
            return value
        except ValueError:
            # anything that can't be converted to an Integer
            return None

    def to_xml(self, value):
        if not self._check_range(value):
            raise Exception("Integer field value '%s' is not in authorized ranges '%s'" % (value, self.ranges))
        return super(IntegerMapper, self).to_xml(value)

class UUIDMapper(fields.StringMapper):

    def to_python(self, node):
        value = super(UUIDMapper, self).to_python(node)
        if value and not UUID.validate(value):
            raise Exception("Invalid UUID field value '%s'" % (value,))
        return value

    def to_xml(self, value):
        if value and not UUID.validate(value):
            raise Exception("Invalid UUID field value '%s'" % (value,))
        return super(UUIDMapper, self).to_xml(value)

class NameMapper(StringMapper):

    pattern = re.compile("[A-Z0-9_\.\-\\:/]+", re.IGNORECASE)

    def to_python(self, node):
        value = super(NameMapper, self).to_python(node)
        if not NameMapper.pattern.match(value):
            raise Exception("Invalid Name field value '%s'" % (value,))
        return value

    def to_xml(self, value):
        if not NameMapper.pattern.match(value):
            raise Exception("Invalid Name field value '%s'" % (value,))
        return super(NameMapper, self).to_xml(value)

class AbsFilePathMapper(StringMapper):

    pattern = re.compile("/[A-Z0-9_\.\+\-\"\'\<\>/%,]+", re.IGNORECASE)

    def to_python(self, node):
        value = super(AbsFilePathMapper, self).to_python(node)
        if value and not self.__class__.pattern.match(value):
            raise Exception("Invalid absolute file path field value '%s'" % (value,))
        return value

    def to_xml(self, value):
        if value and not self.__class__.pattern.match(value):
            raise Exception("Invalid absolute file path field value '%s'" % (value,))
        return super(AbsFilePathMapper, self).to_xml(value)

class FilePathMapper(AbsFilePathMapper):
    
    pattern = re.compile("[A-Z0-9_\.\+\-\"\'\<\>/%]+", re.IGNORECASE)


##############################################################################
# Fields
##############################################################################

class Field(fields.Field): pass
class SimpleBooleanField(fields.SimpleBooleanField): pass
class NodeField(fields.NodeField): pass
class NodeListField(fields.NodeListField): pass
class ItemField(fields.ItemField): pass
class DateTimeField(fields.DateTimeField): pass
class DateTimeListField(fields.DateTimeListField): pass
class DateField(fields.DateField): pass
class DateListField(fields.DateListField): pass
class SchemaField(fields.SchemaField): pass

class DictField(Field):
    """Base class for all xmlmap fields.

    Takes an optional ``required`` value to indicate that the field is required
    or not required in the XML.  By default, required is ``None``, which indicates
    that it is unknown whether the field is required or not.  The required value
    for an xmlmap field should not conflict with the schema or DTD for that xml,
    if there is one.
    """

    # track each time a Field instance is created, to retain order
    creation_counter = 0

    def __init__(self, xpath, manager, mapper, required=None, verbose_name=None,
                    help_text=None):
        # compile xpath in order to catch an invalid xpath at load time
        if isinstance(xpath, dict):
            for key, value in xpath.items():
                etree.XPath(value)
        else:
            etree.XPath(xpath)
        # NOTE: not saving compiled xpath because namespaces must be
        # passed in at compile time when evaluating an etree.XPath on a node
        self.xpath = xpath
        self.manager = manager
        self.mapper = mapper
        self.required = required
        self.verbose_name = verbose_name
        self.help_text = help_text

        # pre-parse the xpath for setters, etc
        if isinstance(xpath, dict):
            self.parsed_xpath = dict()
            for key, value in xpath.items():
                self.parsed_xpath[key] = parse(value)
        else:
            self.parsed_xpath = parse(xpath)

        # adjust creation counter, save local copy of current count
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

class StringField(Field):

    """Map an XPath expression to a single Python string. If the XPath
    expression evaluates to an empty NodeList, a StringField evaluates to
    `None`.

    Takes an optional parameter to indicate that the string contents should have
    whitespace normalized.  By default, does not normalize.

    Takes an optional list of choices to restrict possible values.

    Supports setting values for attributes, empty nodes, or text-only nodes.
    """

    def __init__(self, xpath, normalize=False, choices=None, *args, **kwargs):
        self.choices = choices
        # FIXME: handle at a higher level, common to all/more field types?
        #        does choice list need to be checked in the python ?
        super(StringField, self).__init__(xpath,
                manager = SingleNodeManager(),
                mapper = StringMapper(normalize=normalize, choices=choices), *args, **kwargs)


class StringListField(Field):

    """Map an XPath expression to a list of Python strings. If the XPath
    expression evaluates to an empty NodeList, a StringListField evaluates to
    an empty list.


    Takes an optional parameter to indicate that the string contents should have
    whitespace normalized.  By default, does not normalize.

    Takes an optional list of choices to restrict possible values.

    Actual return type is :class:`~eulxml.xmlmap.fields.NodeList`, which can be
    treated like a regular Python list, and includes set and delete functionality.
    """
    def __init__(self, xpath, normalize=False, choices=None, *args, **kwargs):
        self.choices = choices
        super(StringListField, self).__init__(xpath,
                manager = NodeListManager(),
                mapper = StringMapper(normalize=normalize, choices=choices), *args, **kwargs)


class IntegerField(Field):

    """Map an XPath expression to a single Python integer. If the XPath
    expression evaluates to an empty NodeList, an IntegerField evaluates to
    `None`.

    Supports setting values for attributes, empty nodes, or text-only nodes.
    """

    def __init__(self, xpath, ranges=None, *args, **kwargs):
        self.ranges = ranges
        super(IntegerField, self).__init__(xpath,
                manager = SingleNodeManager(),
                mapper = IntegerMapper(ranges=ranges), *args, **kwargs)

class IntegerListField(Field):

    """Map an XPath expression to a list of Python integers. If the XPath
    expression evaluates to an empty NodeList, an IntegerListField evaluates to
    an empty list.

    Actual return type is :class:`~eulxml.xmlmap.fields.NodeList`, which can be
    treated like a regular Python list, and includes set and delete functionality.
    """

    def __init__(self, xpath, ranges=None, *args, **kwargs):
        self.ranges = ranges
        super(IntegerListField, self).__init__(xpath,
                manager = NodeListManager(),
                mapper = IntegerMapper(ranges=ranges), *args, **kwargs)

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
