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
