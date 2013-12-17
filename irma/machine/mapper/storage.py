import fields

from eulxml import xmlmap

_formatdev  = ["none", "auto", "ext2", "ext3", "ext4", "ufs", "iso9660", "udf", "gfs", "gfs2", "vfat", "hfs+", "xfs"]
_formatfile = ["raw", "dir", "bochs", "cloop", "cow", "dmg", "iso", "qcow", "qcow2", "vmdk", "vpc"]
_sizingunit = ["B", "KB", "K", "KiB", "MB", "M", "MiB", "G", "GB", "GiB", "T", "TB", "TiB", "P", "PB", "PiB", "E", "EB", "EiB"]

##############################################################################
# Shared structures
##############################################################################

class StoragePermissions(xmlmap.XmlObject):

    ROOT_NAME = 'permissions'

    mode = fields.UnixPermissionField('mode')
    owner = fields.UnixPermissionField('owner')
    group = fields.UnixPermissionField('group')
    label = fields.StringField('label')

class StorageEncryption(xmlmap.XmlObject):

    ROOT_NAME = 'encryption'

    format = fields.StringField('@format', choices=["default", "qcow"])
    type = fields.StringField('secret/@type', choices=["passphrase"])
    uuid = fields.UUIDField('secret/@uuid')

## xml = """
## <encryption format='qcow'>
##     <secret type='passphrase' uuid='c1f11a6d-8c5d-4a3e-ac7a-4e171c5e0d4a' />
## </encryption>
## """
## 
## xml = xmlmap.load_xmlobject_from_string(xml, xmlclass=StorageEncryption)
## print xml.format
## print xml.type
## print xml.uuid
## 
## print xml.serialize(pretty=True)
## 
## xml = StorageEncryption()
## xml.format = "default"
## xml.type = "passphrase"
## xml.uuid = "39c78a8f-bd58-403b-b904-8a4411d804a0"
## 
## print xml.serialize(pretty=True)


##############################################################################
# Storage Volume specific structures
##############################################################################

class StorageVolumeDeviceExtent(xmlmap.XmlObject):

    ROOT_NAME = 'extent'

    start = fields.IntegerField('@start')
    end = fields.IntegerField('@end')

class StorageVolumeSource(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    path = fields.AbsFilePathField('path')
    devextents = fields.NodeListField('extent', StorageVolumeDeviceExtent)

class StorageVolumeTarget(xmlmap.XmlObject):

    ROOT_NAME = 'target'

    path = fields.AbsFilePathField('path')
    format = fields.StringField('type', choices=sum([_formatdev, _formatfile], []))
    permissions = fields.NodeField('permissions', StoragePermissions)
    encryption = fields.NodeField('encryption', StorageEncryption)

class StorageBackingStore(xmlmap.XmlObject):

    ROOT_NAME = 'backingStore'
    
    path = fields.AbsFilePathField('path')
    format = fields.StringField('type', choices=sum([_formatdev, _formatfile], []))
    permissions = fields.NodeField('permissions', StoragePermissions)

class StorageVolume(xmlmap.XmlObject):

    ROOT_NAME = 'volume'

    # general metadata
    name = fields.NameField("name")
    key = fields.StringField("key")
    # source
    source = fields.NodeListField('source', StorageVolumeSource)
    # sizing
    capacity = fields.IntegerField('capacity')
    allocation = fields.IntegerField('allocation')
    capacity_unit = fields.StringField('capacity/@unit', choices=_sizingunit)
    allocation_unit = fields.StringField('allocation/@unit', choices=_sizingunit)
    # target
    target = fields.NodeField('target', StorageVolumeTarget)
    # backing store
    backingstore = fields.NodeField('backingStore', StorageBackingStore)

## xml = """
## <volume>
##     <name>sparse.img</name>
##     <allocation>0</allocation>
##     <capacity unit="T">1</capacity>
##     <source>
##         <path>/var/location/0</path>
##     </source>
##     <source>
##         <path>/var/location/1</path>
##     </source>
##     <target>
##        	<path>/var/lib/virt/images/sparse.img</path>
##        	<permissions>
##        	    <owner>107</owner>
##             <group>107</group>
##             <mode>0744</mode>
##             <label>virt_image_t</label>
##         </permissions>
##     </target>
##     <backingStore>
##         <path>/var</path>
##         <type>qcow</type>
##         <permissions>
##        	    <owner>107</owner>
##             <group>107</group>
##             <mode>0744</mode>
##             <label>virt_image_t</label>
##         </permissions>
##     </backingStore>
## </volume>
## """
## 
## xml = xmlmap.load_xmlobject_from_string(xml, xmlclass=StorageVolume)
## print xml.name
## print xml.key
## print xml.capacity
## print xml.capacity_unit
## print xml.allocation
## print xml.allocation_unit
## for source in xml.source:
##     print source.path
## print xml.target.path
## print xml.target.permissions.owner
## print xml.target.permissions.group
## print xml.target.permissions.mode
## print xml.target.permissions.label
## print xml.backingstore.path
## print xml.backingstore.format
## print xml.backingstore.permissions.owner
## print xml.backingstore.permissions.group
## print xml.backingstore.permissions.mode
## print xml.backingstore.permissions.label
## print xml.serialize(pretty=True)
## 
## xml = StorageVolume()
## xml.name = "default"
## xml.key = "passphrase"
## xml.allocation = 1000
## xml.allocation_unit = "G"
## xml.capacity = 1000
## xml.capacity_unit = "G"
## xml.source = [StorageVolumeSource()]
## xml.source[0].path = "/var/location/2"
## xml.source[0].devextents = [StorageVolumeDeviceExtent()]
## xml.source[0].devextents[0].start = 100
## xml.source[0].devextents[0].end = 100
## xml.target = StorageVolumeTarget()
## xml.target.path = "/path"
## xml.target.permissions = StoragePermissions()
## xml.target.permissions.owner = 777
## xml.target.permissions.group = 777
## xml.target.permissions.mode = 777
## xml.target.permissions.label = 777
## xml.target.encryption = StorageEncryption()
## xml.target.encryption.format = "qcow"
## xml.backingstore = StorageBackingStore()
## xml.backingstore.path = "/var"
## xml.backingstore.format = "none"
## xml.backingstore.permissions = StoragePermissions()
## xml.backingstore.permissions.owner = 777
## xml.backingstore.permissions.group = 777
## xml.backingstore.permissions.mode = 777
## xml.backingstore.permissions.label = "coucou"
## print xml.serialize(pretty=True)


##############################################################################
# Storage Pool specific structure
##############################################################################

_pooltype = ["dir", "fs", "netfs", "logical", "disk", "iscsi", "scsi", "mpath"]
_fsformat = ["auto", "ext2", "ext3", "ext4", "ufs", "iso9660", "udf", "gfs", "gfs2", "vfat", "hfs+", "xfs", "ocfs2"]
_netfsformat = ["auto", "nfs"]
_logicalformat = ["auto", "lvm2"]
_diskformat = ["none", "dos", "dvh", "gpt", "mac", "bsd", "pc98", "sun", "lvm2"]

class StoragePoolSourceDir(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolDeviceExtent(xmlmap.XmlObject):

    ROOT_NAME = 'freeExtent'

    start = fields.IntegerField('@start')
    end = fields.IntegerField('@end')

class StoragePoolDeviceInfo:

    ROOT_NAME = 'device'

    # infodev
    path = fields.StringField('@path') # TODO: create a new field for this
    devextents = fields.NodeListField('freeExtent', StoragePoolDeviceExtent)

class StoragePoolFsFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    # type
    type = fields.StringField('format/@type', choices=_fsformat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceFs(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infodev
    dev = fields.NodeField('device', StoragePoolDeviceInfo)
    # fmtfs
    format = fields.NodeField('format', StoragePoolFsFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolNetFsFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    # type
    type = fields.StringField('format/@type', choices=_netfsformat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceNetFs(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infohost
    host = fields.NameField('host/@name')
    port = fields.IntegerField('host/@port')
    # infodir
    path = fields.AbsFilePathField('dir/@path')
    # fmtnetfs
    format = fields.NodeField('format', StoragePoolNetFsFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceLogicalInfo(xmlmap.XmlObject):

    # infoname
    name = fields.StringField('name')
    # infodev
    dev = fields.NodeField('device', StoragePoolDeviceInfo)

class StoragePoolLogicalFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    # type
    type = fields.StringField('format/@type', choices=_logicalformat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceLogical(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infoname
    name = fields.StringListField('name')
    # infodev
    dev = fields.NodeListField('device', StoragePoolDeviceInfo)
    # fmtlogical
    format = fields.NodeField('format', StoragePoolLogicalFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolDiskFormat(xmlmap.XmlObject):

    ROOT_NAME = 'format'

    # type
    type = fields.StringField('format/@type', choices=_diskformat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceDisk(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infodev
    dev = fields.NodeListField('device', StoragePoolDeviceInfo)
    # fmtdisk
    format = fields.NodeField('format', StoragePoolDiskFormat)
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceIScsi(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infohost
    host = fields.NameField('host/@name')
    port = fields.IntegerField('host/@port')
    # infodev
    dev = fields.NodeListField('device', StoragePoolDeviceInfo)
    # initiatorinfo
    initiator = fields.StringField('initiator/iqn/@name')
    # infoauth
    auth_type = fields.StringField('auth/@type', choices=["chap"])
    auth_login = fields.StringField('auth/@login')
    auth_passwd = fields.StringField('auth/@passwd')
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceScsi(xmlmap.XmlObject):

    ROOT_NAME = 'source'

    # infoadapter
    adapter = fields.StringField('adapter/@name')
    # infovendor
    vendor = fields.StringField('vendor/@name')
    product = fields.StringField('product/@name')

class StoragePoolSourceMpath(xmlmap.XmlObject):

    ROOT_NAME = 'source'

class StoragePoolTarget(xmlmap.XmlObject):

    ROOT_NAME = 'target'

    path = fields.AbsFilePathField('path')
    permissions = fields.NodeField('permissions', StoragePermissions)

class StoragePool(xmlmap.XmlObject):

    ROOT_NAME = 'pool'

    type = fields.StringField("@type", choices=_pooltype)
    # general metadata
    name = fields.NameField("name")
    uuid = fields.UUIDField("uuid")
    # source
    source = fields.NodeDictField('source', '@type', {
        'dir'     : fields.NodeMapper(StoragePoolSourceDir), 
        'fs'      : fields.NodeMapper(StoragePoolSourceFs),
        'netfs'   : fields.NodeMapper(StoragePoolSourceNetFs),
        'logical' : fields.NodeMapper(StoragePoolSourceLogical),
        'disk'    : fields.NodeMapper(StoragePoolSourceDisk),
        'iscsi'   : fields.NodeMapper(StoragePoolSourceIScsi),
        'scsi'    : fields.NodeMapper(StoragePoolSourceScsi),
        'mpath'   : fields.NodeMapper(StoragePoolSourceMpath)})
    # sizing
    capacity = fields.IntegerField('capacity')
    allocation = fields.IntegerField('allocation')
    capacity_unit = fields.StringField('capacity/@unit', choices=_sizingunit)
    allocation_unit = fields.StringField('allocation/@unit', choices=_sizingunit)
    available = fields.IntegerField('available')
    available_unit = fields.StringField('available/@unit', choices=_sizingunit)
    # target
    target = fields.NodeField('target', StoragePoolTarget)

## xml = """
## <pool type="dir">
##     <name>virtimages</name>
##     <uuid>3e3fce45-4f53-4fa7-bb32-11f34168b82b</uuid>
##     <allocation>10000000</allocation>
##     <capacity>50000000</capacity>
##     <available>40000000</available>
##     <source>
##         <product name="bb" />
##         <vendor name="bb" />
##     </source>
##     <target>
##        	<path>/var/lib/virt/images/sparse.img</path>
##        	<permissions>
##        	    <owner>107</owner>
##             <group>107</group>
##             <mode>0744</mode>
##             <label>virt_image_t</label>
##         </permissions>
##     </target>
## </pool>
## """
## 
## xml = xmlmap.load_xmlobject_from_string(xml, xmlclass=StoragePool)
## print xml.type
## print xml.name
## print xml.uuid
## print xml.capacity
## print xml.capacity_unit
## print xml.allocation
## print xml.allocation_unit
## print xml.available
## print xml.available_unit
## print xml.source
## print xml.source[xml.type].product
## print xml.source[xml.type].vendor
## print xml.target.path
## print xml.target.permissions.owner
## print xml.target.permissions.group
## print xml.target.permissions.mode
## print xml.target.permissions.label
## print xml.serialize(pretty=True)
## 
## xml = StoragePool()
## xml.type = "fs"
## xml.name = "default"
## xml.uuid = "3e3fce45-4f53-4fa7-bb32-11f34168b82b"
## xml.allocation = 1000
## xml.allocation_unit = "G"
## xml.capacity = 1000
## xml.capacity_unit = "G"
## xml.available = 1000
## xml.available_unit = "G"
## xml.source = [StoragePoolSourceFs()]
## xml.source[xml.type].vendor = "/var/location/2"
## xml.source[xml.type].product = "/var/location/2"
## xml.source[xml.type].devextents = [StorageVolumeDeviceExtent()]
## xml.source[xml.type].devextents[0].start = 100
## xml.source[xml.type].devextents[0].end = 100
## xml.target = StoragePoolTarget()
## xml.target.path = "/path"
## xml.target.permissions = StoragePermissions()
## xml.target.permissions.owner = 777
## xml.target.permissions.group = 777
## xml.target.permissions.mode = 777
## xml.target.permissions.label = 777
## print xml.serialize(pretty=True)
