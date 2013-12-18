import fields, basictypes
import storagevol

from eulxml import xmlmap


class ScaledInteger(storagevol.ScaledInteger): pass
class Permissions(storagevol.Permissions): pass

class Directory(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class DeviceExtent(xmlmap.XmlObject):

    ROOT_NAME = 'freeExtent'

    start = basictypes.UnsignedLongField('@start')
    end = basictypes.UnsignedLongField('@end')

class DeviceInfo(xmlmap.XmlObject):

    ROOT_NAME = 'device'

    # infodev
    path = fields.StringField('@path') # TODO: add choice with pattern here to choose either name or absfilepath
    devextents = fields.NodeField('freeExtent', DeviceExtent)

class FilesystemFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    # constants
    AUTO    = "auto"
    EXT2    = "ext2"
    EXT3    = "ext3"
    EXT4    = "ext4"
    UFS     = "ufs"
    ISO9660 = "iso9660"
    UDF     = "udf"
    GFS     = "gfs"
    GFS2    = "gfs2"
    VFAT    = "vfat"
    HFS     = "hfs+"
    XFS     = "xfs"
    OCFS2   = "ocfs2"

    # type
    type = fields.StringField('format/@type', choices=[AUTO, EXT2, EXT3, EXT4, UFS, ISO9660, UDF, GFS, GFS2, VFAT, HFS, XFS, OCFS2])
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class Filesystem(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infodev
    device = fields.NodeField('device', DeviceInfo)
    # fmtfs
    format = fields.NodeField('format', FilesystemFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class NetFilesystemFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    # constants
    AUTO = "auto"
    NFS  = "nfs"

    # type
    type = fields.StringField('format/@type', choices=[AUTO, NFS])
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class NetFilesystem(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infohost
    host = fields.StringField('host/@name')
    port = basictypes.ShortIntegerField('host/@port')
    # infodir
    path = basictypes.AbsFilePathField('dir/@path')
    # fmtnetfs
    format = fields.NodeField('format', NetFilesystemFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class LogicalFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    AUTO = "auto"
    LVM2 = "lvm2"

    # type
    type = fields.StringField('format/@type', choices=[AUTO, LVM2])
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

# # TODO: Uncomment this when a node group field is available
# class LogicalInfo(xmlmap.XmlObject):
# 
#     # infoname
#     name = fields.StringField('name')
#     # infodev
#     dev = fields.NodeListField('device', DeviceInfo)

class Logical(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # (infoname, infodev)+
    # TODO: create a NodeGroupField, remove name and dev fields then replace it by info
    # info = fields.NodeListField('[name|device]', LogicalInfo)
    name = fields.StringListField('name')
    dev = fields.NodeListField('device', DeviceInfo)
    # fmtlogical
    format = fields.NodeField('format', LogicalFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class DiskFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    NONE = "none"
    DOS  = "dos"
    DVH  = "dvh"
    GPT  = "gpt"
    MAC  = "mac"
    BSD  = "bsd"
    PC98 = "pc98"
    SUN  = "sun"
    LVM2 = "lvm2"

    # type
    type = fields.StringField('format/@type', choices=[NONE, DOS, DVH, GPT, MAC, BSD, PC98, SUN, LVM2])
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class Disk(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infodev
    dev = fields.NodeListField('device', DeviceInfo)
    # fmtdisk
    format = fields.NodeField('format', DiskFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class iSCSI(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # fields
    CHAP = "chap"

    # infohost
    host = fields.StringField('host/@name')
    port = basictypes.ShortIntegerField('host/@port')
    # infodev
    dev = fields.NodeListField('device', DeviceInfo)
    # initiatorinfo
    initiator = fields.StringField('initiator/iqn/@name')
    # infoauth
    type = fields.StringField('auth/@type', choices=[CHAP])
    login = fields.StringField('auth/@login')
    passwd = fields.StringField('auth/@passwd')
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class SCSI(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infoadapter
    adapter = fields.StringField('adapter/@name')
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class MPATH(xmlmap.XmlObject):

    ROOT_NAME = 'source'

class Target(xmlmap.XmlObject):

    ROOT_NAME = 'target'

    path = basictypes.AbsFilePathField('path')
    permissions = fields.NodeField('permissions', Permissions)

class Sizing(xmlmap.XmlObject):

    capacity   = fields.NodeField('.', ScaledInteger)
    allocation = fields.NodeField('.', ScaledInteger)
    available  = fields.NodeField('.', ScaledInteger)

class StoragePool(xmlmap.XmlObject):

    ROOT_NAME = 'pool'

    # constants
    DIR     = "dir"
    FS      = "fs"
    NETFS   = "netfs"
    LOGICAL = "logical"
    DISK    = "disk"
    ISCSI   = "iscsi"
    SCSI    = "scsi"
    MPATH   = "mpath"

    # common metadata
    type = fields.StringField("@type", choices=[DIR, FS, NETFS, LOGICAL, DISK, ISCSI, SCSI, MPATH])
    name = basictypes.NameField("name")
    uuid = basictypes.UUIDField("uuid")
    # source
    source = fields.NodeDictField('source', '@type', {
        DIR     : fields.NodeMapper(Directory), 
        FS      : fields.NodeMapper(Filesystem),
        NETFS   : fields.NodeMapper(NetFilesystem),
        LOGICAL : fields.NodeMapper(Logical),
        DISK    : fields.NodeMapper(Disk),
        ISCSI   : fields.NodeMapper(iSCSI),
        SCSI    : fields.NodeMapper(SCSI),
        MPATH   : fields.NodeMapper(MPATH)})
    # sizing
    sizing = fields.NodeField('.', Sizing)
    # target
    target = fields.NodeField('target', Target)
