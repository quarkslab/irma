import fields
import basictypes

from eulxml import xmlmap

class Secret(xmlmap.XmlObject):

    ROOT_NAME = 'secret'

    # type constant
    PASSPHRASE = "passphrase"

    # fields
    type   = fields.StringField('@type', choices=[PASSPHRASE])
    uuid   = basictypes.UUIDField('@uuid')

class Encryption(xmlmap.XmlObject):

    ROOT_NAME = 'encryption'

    # format constants
    DEFAULT = "default"
    QCOW    = "qcow"

    # fields
    format = fields.StringField('@format', choices=[DEFAULT, QCOW])
    secret = fields.NodeListField('secret', Secret)
