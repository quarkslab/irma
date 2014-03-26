import uuid, re, random

class UUID(object):

    pattern = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', re.IGNORECASE)

    @classmethod
    def validate(cls, val):
        try:
            uuid.UUID(val)
        except:
            return False
        return True

    @classmethod
    def generate(cls):
        return str(uuid.uuid4())

    @classmethod
    def normalize(cls, val):
        return str(uuid.UUID(val))

class MAC(object):

    pattern = re.compile("[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}", re.IGNORECASE)

    @classmethod
    def validate(cls, val):
        if MAC.pattern.match(val.strip()):
            return True
        return False

    @classmethod
    def generate(cls, oui=None):
        if not oui or len(oui) != 3 or \
            not reduce(lambda x, y: x and y, map(lambda x: isinstance(x, int), oui)):
            oui = [0x00, 0x16, 0x3e] # Xensource, Inc.
        mac = []
        mac.extend(map(lambda x: x % 255, oui))
        mac.extend([ random.randint(0x00, 0x7f),
                     random.randint(0x00, 0xff),
                     random.randint(0x00, 0xff) ])
        return ':'.join(map(lambda x: "%02x" % x, mac))

    @classmethod
    def normalize(cls, val):
        return str(val)

# author liudmil-mitev
# source https://github.com/liudmil-mitev/experiments/blob/master/time/humanize_time.py

INTERVALS = [1, 60, 3600, 86400, 604800, 2419200, 29030400]
NAMES = [('second', 'seconds'),
         ('minute', 'minutes'),
         ('hour', 'hours'),
         ('day', 'days'),
         ('week', 'weeks'),
         ('month', 'months'),
         ('year', 'years')]

def humanize_time(amount, units):
    """
    Divide `amount` in time periods.
    Useful for making time intervals more human readable.

    >>> humanize_time(173, 'hours')
    [(1, 'week'), (5, 'hours')]
    >>> humanize_time(17313, 'seconds')
    [(4, 'hours'), (48, 'minutes'), (33, 'seconds')]
    >>> humanize_time(90, 'weeks')
    [(1, 'year'), (10, 'months'), (2, 'weeks')]
    >>> humanize_time(42, 'months')
    [(3, 'years'), (6, 'months')]
    >>> humanize_time(500, 'days')
    [(1, 'year'), (5, 'months'), (3, 'weeks'), (3, 'days')]
    """
    result = []

    unit = map(lambda a: a[1], NAMES).index(units)
    # Convert to seconds
    amount = amount * INTERVALS[unit]

    for i in range(len(NAMES) - 1, -1, -1):
        a = amount / INTERVALS[i]
        if a > 0:
            result.append((a, NAMES[i][1 % a]))
            amount -= a * INTERVALS[i]
    return result

def humanize_time_str(amount, units):
    res = []
    for (value, unit) in humanize_time(amount, units):
        res.append("{0} {1}".format(value, unit))
    return ", ".join(res)
