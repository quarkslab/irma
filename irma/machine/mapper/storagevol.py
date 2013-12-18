import fields
import basictypes

from storageencryption import Encryption
from eulxml import xmlmap

class ScaledInteger(xmlmap.XmlObject):

    # constants
    B   = "B"
    KB  = "KB"
    K   = "K"
    KiB = "KiB"
    MB  = "MB"
    M   = "M"
    MiB = "MiB"
    G   = "G"
    GB  = "GB"
    GiB = "GiB"
    T   = "T"
    TB  = "TB"
    TiB = "TiB"
    P   = "P"
    PB  = "PB"
    PiB = "PiB"
    E   = "E"
    EB  = "EB"
    EiB = "EiB"

    # fields
    unit = basictypes.UnsignedLongField('capacity')
    size = fields.StringField('capacity/@unit', choices=
            [ B, K, KB, KiB, M, MB, MiB, G, GB, GiB, T, TB, TiB, P, PB, PiB, E, EB, EiB ])

class Sizing(xmlmap.XmlObject):

    capacity   = fields.NodeField('.', ScaledInteger)
    allocation = fields.NodeField('.', ScaledInteger)

class Permissions(xmlmap.XmlObject):

    ROOT_NAME = 'permissions'

    mode  = basictypes.UnixPermissionField('mode')
    owner = basictypes.UnixPermissionField('owner')
    group = basictypes.UnixPermissionField('group')
    label = fields.StringField('label')

class Target(xmlmap.XmlObject):

    ROOT_NAME = 'target'

    # device constants
    NONE    = "none"
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

    # file constants
    RAW     = "raw"
    DIR     = "dir"
    BOCHS   = "bochs"
    CLOOP   = "cloop"
    QCOW    = "cow"
    DMG     = "dmg"
    ISO     = "iso"
    QCOW    = "qcow"
    QCOW2   = "qcow2"
    VMDK    = "vmdk"
    VPC     = "vpc"

    # fields
    path = basictypes.AbsFilePathField('path')
    type = fields.StringField('format/@type', choices=sum(
        [[ NONE, AUTO, EXT2, EXT3, EXT4, UFS, ISO9660, UDF, GFS, GFS2, VFAT, HFS, XFS ],
         [ RAW, DIR, BOCHS, CLOOP, QCOW, DMG, ISO, QCOW, QCOW2, VMDK, VPC ]], []))
    permissions = fields.NodeField('permissions', Permissions)
    encryption  = fields.NodeField('encryption', Encryption)

class BackingStore(xmlmap.XmlObject):

    ROOT_NAME = 'backingStore'
    
    # device constants
    NONE    = Target.NONE 
    AUTO    = Target.AUTO 
    EXT2    = Target.EXT2 
    EXT3    = Target.EXT3 
    EXT4    = Target.EXT4 
    UFS     = Target.UFS 
    ISO9660 = Target.ISO9660 
    UDF     = Target.UDF 
    GFS     = Target.GFS 
    GFS2    = Target.GFS2 
    VFAT    = Target.VFAT 
    HFS     = Target.HFS 
    XFS     = Target.XFS 

    # file constants
    RAW     = Target.RAW 
    DIR     = Target.DIR 
    BOCHS   = Target.BOCHS 
    CLOOP   = Target.CLOOP 
    QCOW    = Target.QCOW 
    DMG     = Target.DMG 
    ISO     = Target.ISO 
    QCOW    = Target.QCOW 
    QCOW2   = Target.QCOW2 
    VMDK    = Target.VMDK 
    VPC     = Target.VPC 

    # fields
    path = basictypes.AbsFilePathField('path')
    type = fields.StringField('type', choices=sum(
        [[ NONE, AUTO, EXT2, EXT3, EXT4, UFS, ISO9660, UDF, GFS, GFS2, VFAT, HFS, XFS ],
         [ RAW, DIR, BOCHS, CLOOP, QCOW, DMG, ISO, QCOW, QCOW2, VMDK, VPC ]], []))
    permissions = fields.NodeField('permissions', Permissions)

class DeviceExtent(xmlmap.XmlObject):

    ROOT_NAME = 'extent'

    start = basictypes.UnsignedLongField('@start')
    end   = basictypes.UnsignedLongField('@end')

class Source(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    path = basictypes.AbsFilePathField('path')
    devextents = fields.NodeListField('extent', DeviceExtent)

class StorageVolume(xmlmap.XmlObject):

    ROOT_NAME = 'volume'

    name   = basictypes.NameField('name')
    key    = fields.StringField('key')
    source = fields.NodeListField('source', Source)
    sizing = fields.NodeField('.', Sizing)
    target = fields.NodeField('target', Target)
    backingStore = fields.NodeField('backingStore', BackingStore)
