import hashlib
import config.parser as config
from irma.common.exceptions import IrmaValueError
from lib.common.compat import timestamp
from lib.irma.database.nosqlobjects import NoSQLDatabaseObject
from lib.irma.fileobject.handler import FileObject
from lib.irma.common.utils import IrmaScanStatus, IrmaLockMode
from lib.irma.common.exceptions import IrmaDatabaseError

cfg_dburi = config.get_db_uri()
cfg_dbname = config.frontend_config['mongodb'].dbname
cfg_coll = config.frontend_config['collections']

class ScanInfo(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_info

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.user = None
        self.date = timestamp()
        self.oids = {}
        self.probelist = None
        self.status = IrmaScanStatus.created
        super(ScanInfo, self).__init__(**kwargs)

    def update_status(self, status):
        self.status = status
        self.update({'status':self.status})

    def is_completed(self):
        probelist = self.probelist
        for fileinfo in self.oids.values():
            remaining = [probe for probe in probelist if probe not in fileinfo['probedone']]
            if len(remaining) != 0:
                # at least one result is not there
                return False
        return True

    def get_results(self):
        res = {}
        for (oid, info) in self.oids.items():
            name = info['name']
            r = ScanResults(id=oid, mode=IrmaLockMode.read)
            if r.results:
                scanfile = ScanFile(id=oid)
                sha256 = scanfile.hashvalue
                res[sha256] = {}
                res[sha256]['filename'] = name
                res[sha256]['results'] = dict((probe, results) for (probe, results) in r.results.iteritems() if probe in self.probelist)
        return res

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(ScanInfo, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(ScanInfo, cls).is_lock_free(id)

    @classmethod
    def find_old_instances(cls):
        return super(ScanInfo, cls).find(
            {'date': {'$lt': timestamp() - config.frontend_config['cron_frontend']['clean_db_scan_info_max_age']}},
            ['_id']
        )


class ScanResults(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_results

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.probelist = []
        self.results = {}
        super(ScanResults, self).__init__(**kwargs)

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(ScanResults, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(ScanResults, cls).is_lock_free(id)

    @classmethod
    def init_id(cls, id, **kwargs):
        return super(ScanResults, cls).init_id(id, **kwargs)


class ScanFile(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_files

    def __init__(self, dbname=None, sha256=None, id=None, **kwargs):
        """Constructor
        :param sha256: The sha256 of the object to load (priority over the id)
        :param id: The id of the object to load
        """

        if dbname:
            self._dbname = dbname

        if id:
            super(ScanFile, self).__init__(id=id, **kwargs)
        else:
            super(ScanFile, self).__init__(**kwargs)
            if sha256:
                self.load(self.get_id_by_sha256(sha256))
            else:
                self.sha256 = None
                self.sha1 = None
                self.md5 = None
                self.date_upload = None
                self.date_last_scan = None
                self.size = None
                self.filename = None
                self.alt_filenames = []
                self.file_oid = None

    def save(self, data, name):
        self.sha256 = hashlib.sha256(data).hexdigest()
        self.sha1 = hashlib.sha1(data).hexdigest()
        self.md5 = hashlib.md5(data).hexdigest()

        _id = self.get_id_by_sha256(self.sha256)
        if not _id:
            file_data = ScanFileData()
            file_data.save(data, name)
            self.date_upload = timestamp()
            self.date_last_scan = self.date_upload
            self.size = file_data.length
            self.filename = name
            self.file_oid = file_data.id
            super(ScanFile, self).save()
        else:
            self.load(_id)
            self.date_last_scan = timestamp()
            if name not in self.alt_filenames:
                self.alt_filenames.append(name)
            # if file has been deleted -> save again
            if self.file_oid is None:
                file_data = ScanFileData()
                file_data.save(data, name)
                self.file_oid = file_data.id
            self.update()

    @classmethod
    def _get_id_by_sha256(cls, sha256):
        res = cls.find({'sha256': sha256}, ['_id'])
        if len(res) > 1:
            raise IrmaDatabaseError("Multiple entries in ScanFile with same sha256 value")
        # FIXME when empty res == None or res == [] ?
        elif len(res) == 0:
            return None
        else
            return res[0]['_id']

    @property
    def data(self):
        if self.file_oid is None:
            return None
        return ScanFileData(id=self.file_oid).data


class ScanFileData(FileObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection_file = cfg_coll.scan_filedata
