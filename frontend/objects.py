import hashlib
import config.parser as config
from lib.common.compat import timestamp
from lib.irma.common.exceptions import IrmaDatabaseError
from lib.irma.database.nosqlobjects import NoSQLDatabaseObject
from lib.irma.fileobject.handler import FileObject
from lib.irma.common.utils import IrmaScanStatus
from format import format_result

cfg_dburi = config.get_db_uri()
cfg_dbname = config.frontend_config['mongodb'].dbname
cfg_coll = config.frontend_config['collections']


def format_results(res_dict, filter_type=None):
    # filter type is list of type returned
    res = {}
    for probe in res_dict.keys():
        # old results format
        # FIXME: remove this if db is cleaned
        if 'probe_res' in res_dict[probe]:
            probe_res = res_dict[probe]['probe_res']
        else:
            probe_res = res_dict[probe]
        format_res = format_result(probe, probe_res)
        # filter by type
        if filter_type is not None and \
         'type' in format_res and \
         format_res['type'] not in filter_type:
            continue
        res[probe] = format_res
    return res

class ScanResults(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_results

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.name = None
        self.hashvalue = None
        self.results = {}
        super(ScanResults, self).__init__(**kwargs)

    def get_results(self, filter_type=None):
        res = {}
        sha256 = self.hashvalue
        res[sha256] = {}
        res[sha256]['filename'] = self.name
        res[sha256]['results'] = format_results(self.results,
                                                filter_type=filter_type)
        return res

    @property
    def probedone(self):
        return self.results.keys()


class ScanInfo(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_info

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.user = None
        self.date = timestamp()
        self.scanfile_ids = {}
        self.probelist = None
        self.status = IrmaScanStatus.created
        super(ScanInfo, self).__init__(**kwargs)

    def add_file(self, scanfile_id, name, hashvalue):
        scan_res = ScanResults()
        scan_res.name = name
        scan_res.hashvalue = hashvalue
        scan_res.update()
        self.scanfile_ids[scanfile_id] = scan_res.id
        return

    def update_status(self, status):
        self.status = status
        self.update({'status': self.status})

    def is_completed(self):
        probelist = self.probelist
        for res_id in self.scanfile_ids.values():
            scan_res = ScanResults(id=res_id)
            for probe in probelist:
                if probe not in scan_res.probedone:
                    # at least one result is not there
                    return False
        return True

    def get_results(self, filter_type=None):
        res = {}
        for scaninfo_id in self.scanfile_ids.values():
            scan_res = ScanResults(id=scaninfo_id)
            res.update(scan_res.get_results(filter_type=filter_type))
        return res

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(ScanInfo, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(ScanInfo, cls).is_lock_free(id)

    @classmethod
    def remove_old_instances(cls, age):
        found = super(ScanInfo, cls).find(
            {'date': {'$lt': timestamp() - age}},
            ['_id']
        )
        if found.count() == 0:
            return 0
        else:
            for f in found:
                temp_scan_info = ScanInfo.get_temp_instance(f['_id'])
                temp_scan_info.remove()
            return found.count()


class ScanRefResults(NoSQLDatabaseObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_ref_results

    def __init__(self, dbname=None, **kwargs):
        if dbname:
            self._dbname = dbname
        self.results = {}
        super(ScanRefResults, self).__init__(**kwargs)

    @classmethod
    def has_lock_timed_out(cls, id):
        return super(ScanRefResults, cls).has_lock_timed_out(id)

    @classmethod
    def is_lock_free(cls, id):
        return super(ScanRefResults, cls).is_lock_free(id)

    @classmethod
    def init_id(cls, id, **kwargs):
        return super(ScanRefResults, cls).init_id(id, **kwargs)

    @property
    def probelist(self):
        return self.results.keys()

    def get_results(self, filter_type=None):
        res = {}
        if self.results:
            scanfile = ScanFile(id=self.id)
            sha256 = scanfile.hashvalue
            res[sha256] = {}
            res[sha256]['filename'] = " - ".join(scanfile.alt_filenames)
            res[sha256]['results'] = format_results(self.results,
                                                    filter_type=filter_type)
            res[sha256]['nb_scan'] = len(scanfile.scan_id)
            res[sha256]['date_upload'] = scanfile.date_upload
            res[sha256]['date_last_scan'] = scanfile.date_last_scan
        return res


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
                _oid = self._get_id_by_sha256(sha256)
                if _oid is None:
                    raise IrmaDatabaseError("sha256 not found")
                else:
                    self.load(_oid)
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
                self.scan_id = []

    def save(self, data, name):
        self.sha256 = hashlib.sha256(data).hexdigest()
        self.sha1 = hashlib.sha1(data).hexdigest()
        self.md5 = hashlib.md5(data).hexdigest()

        _id = self._get_id_by_sha256(self.sha256)
        if not _id:
            file_data = ScanFileData()
            file_data.save(data, name)
            self.date_upload = timestamp()
            self.date_last_scan = self.date_upload
            self.size = len(data)
            self.filename = name
            self.alt_filenames.append(name)
            self.file_oid = file_data.id
            self.scan_id = []
        else:
            self.load(_id)
            if name not in self.alt_filenames:
                self.alt_filenames.append(name)
            if self.file_oid is None:   # if deleted, save again
                file_data = ScanFileData()
                file_data.save(data, self.filename)
                self.file_oid = file_data.id
        self.update()

    def delete_data(self):
        if self.file_oid is not None:
            ScanFileData(self.file_oid).delete()
            self.file_oid = None
            self.update()
            return True
        return False

    @classmethod
    def _get_id_by_sha256(cls, sha256):
        res = cls.find({'sha256': sha256}, ['_id'])
        if res.count() > 1:
            raise IrmaDatabaseError("Multiple ScanFile with same sha256 value")
        elif res.count() == 0:
            return None
        else:
            return res[0]['_id']

    @property
    def data(self):
        if self.file_oid is None:
            return None
        return ScanFileData(id=self.file_oid).data

    @property
    def hashvalue(self):
        # used for unicity and ftp integrity
        return self.sha256

    @classmethod
    def remove_old_instances(cls, age):
        found = super(ScanFile, cls).find(
            {'date_upload': {'$lt': timestamp() - age}},
            ['_id']
        )
        nb_deleted = 0
        if found.count() == 0:
            return nb_deleted
        else:
            for f in found:
                temp_scan_file = ScanFile.get_temp_instance(f['_id'])
                if temp_scan_file.delete_data():
                    nb_deleted += 1
            return nb_deleted


class ScanFileData(FileObject):
    _uri = cfg_dburi
    _dbname = cfg_dbname
    _collection = cfg_coll.scan_filedata
