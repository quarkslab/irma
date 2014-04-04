import time


def timestamp():
    """ On some systems, time.time() returns a float
    instead of an int. This function always returns an int
    :rtype: int
    :return: the current timestamp
    """
    return int(str(time.time()).split('.')[0])
