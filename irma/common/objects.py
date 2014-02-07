
class AttributeDictionary(dict):
    """A dictionnary with object-like accessors"""

    __getattr__ = lambda obj, key: obj.get(key, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

