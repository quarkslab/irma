import logging, hashlib, leveldb, binascii, json, argparse

log = logging.getLogger(__name__)


class NSRLDatabase(object):

    ##########################################################################
    # constructor and destructor stuff
    ##########################################################################

    def __init__(self, database, *args, **kwargs):
        self.database = database
        self._database = leveldb.LevelDB(database, *args, **kwargs)

    ##########################################################################
    # constants, for new records, override these variables
    ##########################################################################

    row_as_key = None
    entry_fields = []

    ##########################################################################
    # public methods
    ##########################################################################
    
    def get(self, key):
        try:
            value = self._database.Get(self.serialize_key(key))
            value = self.deserialize_value(value)
        except KeyError:
            value = None
        return value

    @classmethod
    def create_database(cls, rcdfile, dbfile):

        # import specific modules
        import itertools, collections
        from csv import DictReader

        # import internal helpers
        def count_items(iterable):
            """Consume an iterable not reading it into memory;"""
            # clone iterator, and count using the clone
            counter = itertools.count()
            collections.deque(itertools.izip(iterable, counter), maxlen=0) # (consume at C speed)
            return next(counter)

        commit_threshold = 1000
        log_threshold = 50000
        
        try:
            # create database
            database = leveldb.LevelDB(dbfile)
            db_handle = leveldb.WriteBatch()
            # open file 
            csv_file = open(rcdfile, 'r')
            csv_entries = DictReader(csv_file)
            # duplicate iterator and count number of entries
            csv_entries, _csv_entries = itertools.tee(csv_entries)
            csv_count = count_items(_csv_entries)
            # process entries
            for index, row in enumerate(csv_entries):
                # get key and value, then format them
                key = cls.serialize_key(row.pop(cls.row_as_key))
                value = cls.serialize_value(row)
                log.debug("key = {0}, value = {1}".format(cls.deserialize_key(key), cls.deserialize_value(value)))
                # append to queue
                db_handle.Put(key, str(value))
                # commit if threshold 
                if (index % commit_threshold) == 0:
                    database.Write(db_handle, sync=True)
                    del db_handle
                    db_handle = leveldb.WriteBatch()
                # enventually, log to get status
                if (index % log_threshold) == 0:
                    log.info("Current progress: {0}/{1}".format(index, csv_count))
            # commit remaining data
            database.Write(db_handle, sync=True)
        except Exception as e:
            log.exception("{0}".format(str(e)))
            leveldb.DestroyDB(dbfile)

    @classmethod
    def serialize_value(cls, value):
        return json.dumps(map(lambda x: value.get(x.decode("latin1")), cls.entry_fields))

    @classmethod
    def deserialize_value(cls, value):
        value = json.loads(value)
        return dict((field, value[index]) for index, field in enumerate(cls.entry_fields))

    @classmethod
    def serialize_key(cls, key):
        return str(key)

    @classmethod
    def deserialize_key(cls, key):
        return str(key)

class NSRLFileRecord(NSRLDatabase):

    ##########################################################################
    # overriden variables
    ##########################################################################

    row_as_key = "SHA-1"
    entry_fields = ["MD5", "CRC32", "FileName", "FileSize", "ProductCode", "OpSystemCode", "SpecialCode"]

    ##########################################################################
    # public methods
    ##########################################################################

    @classmethod
    def serialize_key(cls, key):
        return binascii.unhexlify(key)

    @classmethod
    def deserialize_key(cls, key):
        return binascii.hexlify(key)


class NSRLOsRecord(NSRLDatabase):

    ##########################################################################
    # overriden variables
    ##########################################################################

    row_as_key = "OpSystemCode"
    entry_fields = ["OpSystemName", "OpSystemVersion", "MfgCode"]


class NSRLManufacturerRecord(NSRLDatabase):

    ##########################################################################
    # overriden variables
    ##########################################################################

    row_as_key = "MfgCode"
    entry_fields = [ "MfgName" ]


class NSRLProductRecord(NSRLDatabase):

    ##########################################################################
    # overriden variables
    ##########################################################################

    row_as_key = "ProductCode"
    entry_fields = ["ProductName", "ProductVersion", "OpSystemCode", "MfgCode", "Language", "ApplicationType"]


class NSRL(object):

    def __init__(self, file, product, os, manufacturer):
        self._db_os = NSRLOsRecord(os)
        self._db_manufacturer = NSRLManufacturerRecord(manufacturer)
        self._db_file = NSRLFileRecord(file)
        self._db_product = NSRLProductRecord(product)

    # TODO: make jointure cleverly than the following
    def getBySHA1(self, sha1):
        file = self._db_file.get(sha1)
        if file:
            values = self._db_product.get(file['ProductCode'])
            if values:
                file.update(values)
            else:
                log.warning("Product record {0} not found for sha1 {1}".format(file['ProductCode'], sha1))
            values = self._db_os.get(file['OpSystemCode'])
            if values:
                file.update(values)
            else:
                log.warning("OS record {0} not found for sha1 {1}".format(file['OpSystemCode'], sha1))
            values = self._db_manufacturer.get(file['MfgCode'])
            if values:
                file.update(values)
            else:
                log.warning("Manufacturer record {0} not found for sha1 {1}".format(file['MfgCode'], sha1))
        return file


##############################################################################
# CLI for debug purposes
##############################################################################

def nsrl_create_database(**kwargs):
    cls = None

    if kwargs["type"] == 'file':
        cls = NSRLFileRecord
    elif kwargs["type"] == 'os':
        cls = NSRLOsRecord
    elif kwargs["type"] == 'manufacturer':
        cls = NSRLManufacturerRecord
    elif kwargs["type"] == 'product':
        cls = NSRLProductRecord

    cls.create_database(kwargs['filename'], kwargs['database'])


def nsrl_get(**kwargs):

    cls = None

    if kwargs["type"] == 'file':
        cls = NSRLFileRecord
    elif kwargs["type"] == 'os':
        cls = NSRLOsRecord
    elif kwargs["type"] == 'manufacturer':
        cls = NSRLManufacturerRecord
    elif kwargs["type"] == 'product':
        cls = NSRLProductRecord

    database = cls(kwargs['database'], block_cache_size=1<<30, max_open_files=3000)
    value = database.get(kwargs['key'])
    print("key {0}: value {1}".format(kwargs['key'], value))


def nsrl_resolve(**kwargs):

    handle = NSRL(kwargs['file'], kwargs['product'], kwargs['os'], kwargs['manufacturer'])
    print handle.getBySHA1(kwargs['sha1'])

if __name__ == '__main__':

    # define command line arguments
    parser = argparse.ArgumentParser(description='NSRL database module CLI mode')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the create parser
    create_parser = subparsers.add_parser('create', help='create NSRL records into a database')
    create_parser.add_argument('-t' , '--type', type=str, choices=['file', 'os', 'manufacturer', 'product'], help='type of the record')
    create_parser.add_argument('filename', type=str, help='filename of the NSRL record')
    create_parser.add_argument('database', type=str, help='database to store NSRL records')
    create_parser.set_defaults(func=nsrl_create_database)

    # create the scan parser
    get_parser = subparsers.add_parser('get', help='get the entry from database')
    get_parser.add_argument('-t' , '--type', type=str, choices=['file', 'os', 'manufacturer', 'product'], help='type of the record')
    get_parser.add_argument('database', type=str, help='database to read NSRL records')
    get_parser.add_argument('key', type=str, help='key to retreive')
    get_parser.set_defaults(func=nsrl_get)

    # create the scan parser
    get_parser = subparsers.add_parser('resolve', help='resolve from sha1')
    get_parser.add_argument('file', type=str, help='filename for file records')
    get_parser.add_argument('product', type=str, help='filename for product records')
    get_parser.add_argument('os', type=str, help='filename for os records')
    get_parser.add_argument('manufacturer', type=str, help='filename for manufacturer records')
    get_parser.add_argument('sha1', type=str, help='sha1 to lookup')
    get_parser.set_defaults(func=nsrl_resolve)

    args = parser.parse_args()

    # set verbosity
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs with only the specific arguments
    # for each subfunction useful for interactive mode.
    func(**args)
