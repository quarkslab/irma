import types


##############################################################################
# Singleton Design Pattern
##############################################################################

class SingletonMetaClass(type):
    """Metaclass for singleton design pattern"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Metaclass compatible with python 2 and 3. Inherit from this for singletons
Singleton = SingletonMetaClass('Singleton', (object, ), {})


##############################################################################
# Parametric Singleton Design Pattern
##############################################################################

class ParametricSingletonMetaClass(type):
    """Metaclass for singleton design pattern"""

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
        if key not in cls._instances:
            cls._instances[key] = super(ParametricSingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls._instances[key]

# Metaclass compatible with python 2 and 3. Inherit from this for parametric
# singletons. Then, pass either an argument "depends_on" in the constructor or
# define a class method called "depends_on" that specifies how to compute the
# parameter value used for the hash table storing the instances:
#
# example with a class method:
# 
# class aParametricSingleton(ParametricSingleton):
#
#     @classmethod
#     def depends_on(*args, **kwargs):
#         return "my key"
#
# example with a lambda wrapped with a class method:
#
# class aParametricSingleton(ParametricSingleton):
#
#     depends_on = classmethod(lambda cls, *args, **kwargs: "my key")

ParametricSingleton = ParametricSingletonMetaClass('ParametricSingleton', (object, ), {})


