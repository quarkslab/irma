import types


##############################################################################
# Singleton Design Pattern
##############################################################################

class SingletonMetaClass(type):
    """Metaclass for singleton design pattern.

    .. warning::

            This metaclass should not be used directly. To declare a class
            using the singleton pattern, one should use the :class:`Singleton`
            class instead.

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Metaclass compatible with python 2 and 3. Inherit from this for singletons
Singleton = SingletonMetaClass('Singleton', (object,), {})
"""Base class for singleton

This class implements the singleton design pattern. One can inherit from this
base class to make a class implement the singleton design pattern.

    .. code-block:: python

        # a class implementing a singleton
        class aParametricSingleton(Singleton):
            
            # do some stuff here
            pass

        # let us verify that it is really a singleton
        print(id(aParametricSingleton())
        print(id(aParametricSingleton())

"""

##############################################################################
# Parametric Singleton Design Pattern
##############################################################################

class ParametricSingletonMetaClass(type):
    """Metaclass for parametric singleton design pattern

    .. warning::

            This metaclass should not be used directly. To declare a class
            using the singleton pattern, one should use the
            :class:`ParametricSingleton` class instead and precise the
            parameter used for the dict using a class method named
            ``depends_on``.

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        # check for "depends_on" attribute
        if not "depends_on" in kwargs and not hasattr(cls, "depends_on"):
            raise TypeError("argument or attribute 'depends_on' not defined")
        # check for unbound methods
        if "depends_on" in kwargs and \
           (not kwargs["depends_on"] or not callable(kwargs["depends_on"])):
            raise TypeError("function in parameter 'depends_on' is not bound")
        elif hasattr(cls, "depends_on") and \
             (not getattr(cls, "depends_on") or not callable(getattr(cls, "depends_on"))):
            raise TypeError("function in attribute 'depends_on' is not bound")

        # call depends_on to get the key
        if "depends_on" in kwargs:
            key = kwargs["depends_on"](cls, args, kwargs)
            del kwargs["depends_on"]
        else:
            key = getattr(cls, "depends_on")(cls, args, kwargs)

        # check for instance
        if cls not in cls._instances:
            cls._instances[cls] = {}
        if key not in cls._instances[cls]:
            cls._instances[cls][key] = super(ParametricSingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls._instances[cls][key]

    def update_key(cls, old_key, new_key):
        cls._instances[cls][new_key] = cls._instances[cls].pop(old_key)

# Metaclass compatible with python 2 and 3. Inherit from this for parametric singletons
ParametricSingleton = ParametricSingletonMetaClass('ParametricSingleton', (object,), {})
"""Base class for parametric singletons

This class implements the parametric singleton design pattern. One can inherit
from this base class to make a class implement a parametric singleton pattern.
Pass either an argument ``depends_on`` in the constructor or define a class
method called ``depends_on`` that specifies how to compute the parameter value
used for the hash table storing the instances:

* example with a **static method**:

.. code-block:: python

    class aParametricSingleton(ParametricSingleton):
  
        @staticmethod
        def depends_on(*args, **kwargs):
            return "my key"

* example with a **``lambda`` wrapped with a static method**:

.. code-block:: python
        
    class aParametricSingleton(ParametricSingleton):

        depends_on = staticmethod(lambda *args, **kwargs: "my key")
"""

class PluginMetaClass(type):
    """Metaclass for auto-registering plugin pattern

    .. warning::

            This metaclass should not be used directly. To declare a class
            using the plugin pattern, one should use the :class:`Plugin` 
            class instead.

    """
    ##########################################################################
    # class constructor
    ##########################################################################

    def __init__(cls, name, bases, attrs):
        # small hack to skip Plugin base class when initializing
        if not len(attrs):
            return
        # Begin to register all classes that derives from Plugin base class
        if not hasattr(cls, '_plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls._plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls._plugins.append(cls)

    ##########################################################################
    # plugin metadata
    ##########################################################################

    _plugin_name = None
    _plugin_version = None
    _plugin_description = None
    _plugin_dependencies = None

    ##########################################################################
    # setters and getters
    ##########################################################################

    @property
    def plugin_name(cls):
        return cls._plugin_name

    @property
    def plugin_version(cls):
        return cls._plugin_version

    @property
    def plugin_description(cls):
        return cls._plugin_description

    @property
    def plugin_dependencies(cls):
        return cls._plugin_dependencies

    @property
    def plugins(cls):
        return cls._plugins

    ##########################################################################
    # utility methods
    ##########################################################################
    
    def get_plugins(cls, *args, **kwargs):
        """return instances of plugins"""
        return [plugin(*args, **kwargs) for plugin in cls._plugins]

    def get_plugin(cls, name, *args, **kwargs):
        """return instance of a named plugin"""
        plugin = filter(lambda x: x.plugin_name == name, cls._plugins)
        return plugin[0] if plugin else None

# Metaclass compatible with python 2 and 3. Inherit from this for Plugins
Plugin = PluginMetaClass('Plugin', (object,), {})
