# Copyright (c) 2014 QuarksLab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import hashlib
import os

from sqlalchemy import Table, Column, Integer, Numeric, ForeignKey, String, \
    event, UniqueConstraint
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import config.parser as config
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaCoreError, IrmaFileSystemError
from lib.common import compat
from lib.common.utils import UUID
from lib.irma.common.utils import IrmaScanStatus, IrmaProbeType
from lib.irma.database.sqlobjects import SQLDatabaseObject
from frontend.models.nosqlobjects import ProbeRealResult
from frontend.helpers.utils import write_sample_on_disk


# SQLite fix for ForeignKey support
# see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
if config.get_sql_db_uri_params()[0] == 'sqlite':
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Auto-create directory for sqlite db
    db_name = os.path.abspath(config.get_sql_db_uri_params()[5])
    dirname = os.path.dirname(db_name)
    if not os.path.exists(dirname):
        print("SQL directory does not exist {0}"
              "..creating".format(dirname))
        os.makedirs(dirname)
        os.chmod(dirname, 0777)
    elif not (os.path.isdir(dirname)):
        print("Error. SQL directory is a not a dir {0}"
              "".format(dirname))
        raise IrmaDatabaseError("Can not create Frontend database dir")

    if not os.path.exists(db_name):
        # touch like method to create a rw-rw-rw- file for db
        open(db_name, 'a').close()
        os.chmod(db_name, 0666)


Base = declarative_base()
tables_prefix = '{0}_'.format(config.get_sql_db_tables_prefix())

# Many to many Tag <-> File
tag_file = Table(
    '{0}tag_file'.format(tables_prefix),
    Base.metadata,
    Column(
        'id_tag',
        Integer,
        ForeignKey('{0}tag.id'.format(tables_prefix))
    ),
    Column(
        'id_file',
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)))
)

# Many to many ProbeResult <-> FileWeb
probe_result_file_web = Table(
    '{0}probeResult_fileWeb'.format(tables_prefix),
    Base.metadata,
    Column(
        'id_fw',
        Integer,
        # see FileWeb.id_file
        ForeignKey('{0}fileWeb.id'.format(tables_prefix))
    ),
    # Removed from FileWeb FK due to SQLite limitation, conceptually it
    # should be a PKF in FileWeb
    # https://groups.google.com/forum/#!topic/sqlalchemy/TxISzgW7xUg
    # Column(
    #     'id_file',
    #     Integer
    # ),
    Column(
        'id_pr',
        Integer,
        ForeignKey('{0}probeResult.id'.format(tables_prefix))
    ),
    # See FileWeb
    # ForeignKeyConstraint(   # Composite PFK from FileWeb
    #     ['id_fw', 'id_file'],
    #     [
    #         '{0}fileWeb.id_fw'.format(tables_prefix),
    #         '{0}fileWeb.id_file'.format(tables_prefix)
    #     ]
    # )
)


class Tag(Base, SQLDatabaseObject):
    __tablename__ = '{0}tag'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    name = Column(
        String,
        nullable=False,
        name='name'
    )

    def __init__(self, name=''):
        super(Tag, self).__init__()
        self.name = name


class File(Base, SQLDatabaseObject):
    __tablename__ = '{0}file'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    sha256 = Column(
        String(length=64),
        index=True,
        name='sha256'
    )
    sha1 = Column(
        String(length=40),
        index=True,
        name='sha1'
    )
    md5 = Column(
        String(length=32),
        index=True,
        name='md5'
    )
    timestamp_first_scan = Column(
        Numeric(asdecimal=False),
        nullable=False,
        name='timestamp_first_scan'
    )
    timestamp_last_scan = Column(
        Numeric(asdecimal=False),
        nullable=False,
        name='timestamp_last_scan'
    )
    size = Column(
        Integer,
        name='size'
    )
    path = Column(
        String(length=255),
        name='path'
    )
    # Many to many Tag <-> File
    tags = relationship(
        'Tag',
        secondary=tag_file,
        backref='files'
    )

    def __init__(self, timestamp_first_scan, timestamp_last_scan, tags=[]):
        super(File, self).__init__()

        self.timestamp_first_scan = timestamp_first_scan
        self.timestamp_last_scan = timestamp_last_scan
        self.tags = tags

    def to_json(self):
        # return only these keys
        keys = ["md5", "sha1", "sha256", "size",
                "timestamp_first_scan", "timestamp_last_scan"]
        return dict((k, v) for (k, v) in self.to_dict().items() if k in keys)

    @classmethod
    def load_from_sha256(cls, sha256, session, data=None):
        """Find the object in the database, update data if file was previously deleted
        :param sha256: the sha256 to look for
        :param session: the session to use
        :param data: the file's data, in case it was deleted (default is None)
        :rtype: cls
        :return: the object that corresponds to the sha256
        :raise: IrmaDatabaseResultNotFound, IrmaDatabaseError,
                IrmaFileSystemError
        """
        try:
            asked_file = session.query(cls).filter(
                cls.sha256 == sha256
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)
        if asked_file.path is None and data is not None:
            asked_file.path = write_sample_on_disk(sha256, data)
        # Note: nothing is done if path is None and data is None too.
        #       Further manipulation of *asked_file* may be dangerous
        return asked_file

    def save_file_to_fs(self, data):
        """Add a sample
        :param data: the sample file
        :raise: IrmaFileSystemError if there is a problem with the filesystem
        """

        sha256 = hashlib.sha256(data).hexdigest()
        # split files between subdirs
        path = write_sample_on_disk(sha256, data)
        self.sha256 = sha256
        self.sha1 = hashlib.sha1(data).hexdigest()
        self.md5 = hashlib.md5(data).hexdigest()
        self.size = len(data)
        self.path = path

    def remove_file_from_fs(self):
        """Remove the sample
        :raise: IrmaFileSystemError if there is a problem with the filesystem
        """
        try:
            if self.path is None:
                return
            os.remove(self.path)
            self.path = None
        except OSError as e:
            raise IrmaFileSystemError(e)

    @classmethod
    def remove_old_files(cls, max_age, session):
        """Remove the files that are older than timestamp() - max_age
        from the file system
        :param max_age: the files older than timestamp() - max_age
            will be deleted
        :rtype: int
        :return: the number of deleted files
        """
        fl = session.query(cls).filter(
            cls.timestamp_last_scan < compat.timestamp() - max_age
        ).filter(
            cls.path is not None
        ).all()
        for f in fl:
            f.remove_file_from_fs()
        return len(fl)

    def get_file_names(self):
        """Fetch the different names of the file
        :rtype: list
        :return: list of filenames
        """
        from_web = []
        for fw in self.files_web:
            from_web.append(fw.name)
        from_submission = []
        for fa in self.files_agent:
            from_submission.append(os.path.split(fa.submission_path)[1])
        return list(set(from_web + from_submission))


class ProbeResult(Base, SQLDatabaseObject):
    __tablename__ = '{0}probeResult'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    type = Column(
        String,
        name='type'
    )
    name = Column(
        String,
        nullable=False,
        name='name'
    )
    nosql_id = Column(
        String,
        name='nosql_id'
    )
    status = Column(
        Integer,
        name='status'
    )
    # Many to many ProbeResult <-> FileWeb
    files_web = relationship(
        'FileWeb',
        secondary=probe_result_file_web,
        backref='probe_results',
        lazy='dynamic',
    )
    # Many to many ProbeResult <-> File
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix))
    )
    file = relationship(
        "File",
        backref=backref('ref_results')
    )

    def __init__(self,
                 type,
                 name,
                 nosql_id,
                 status,
                 file_web=None):
        super(ProbeResult, self).__init__()

        self.type = type
        self.name = name
        self.nosql_id = nosql_id
        self.status = status
        self.files_web = [file_web]

    def get_details(self):
        return ProbeRealResult(id=self.nosql_id)


class Scan(Base, SQLDatabaseObject):
    __tablename__ = '{0}scan'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    external_id = Column(
        String(length=36),
        index=True,
        nullable=False,
        name='external_id'
    )
    date = Column(
        Integer,
        nullable=False,
        name='date'
    )
    ip = Column(
        String,
        name='ip'
    )

    def __init__(self, date, ip):
        super(Scan, self).__init__()
        self.external_id = UUID.generate()
        self.date = date
        self.ip = ip

    @classmethod
    def load_from_ext_id(cls, external_id, session):
        """Find the object in the database
        :param external_id: the id to look for
        :param session: the session to use
        :rtype: cls
        :return: the object that corresponds to the external_id
        :raise: IrmaDatabaseResultNotFound, IrmaDatabaseError
        """
        try:
            return session.query(cls).filter(
                cls.external_id == external_id
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    def finished(self):
        """Tell if the scan is over or not
        :rtype: boolean
        :return: True if the scan is over
        """
        if self.status == IrmaScanStatus.finished:
            return True
        if self.status < IrmaScanStatus.launched:
            return False
        for fw in self.files_web:
            for pr in fw.probe_results:
                if pr.nosql_id is None:
                    return False
        return True

    @property
    def status(self):
        return max(evt.status for evt in self.events)

    @property
    def probes_total(self):
        total = 0
        for fw in self.files_web:
            total += fw.probes_total
        return total

    @property
    def probes_finished(self):
        finished = 0
        for fw in self.files_web:
            finished += fw.probes_finished
        return finished

    def set_status(self, status_code):
        if status_code not in IrmaScanStatus.label.keys():
            raise IrmaCoreError("Trying to update with an unknown status")
        if status_code not in [evt.status for evt in self.events]:
            evt = ScanEvents(status_code, self)
            self.events.append(evt)


class FileWeb(Base, SQLDatabaseObject):
    __tablename__ = '{0}fileWeb'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    scan_file_idx = Column(
        Integer,
        nullable=False,
        name='scan_file_idx'
    )
    # Many to one FileWeb <-> File as part of the primary key
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)),
        nullable=False,
        # conceptually it should be a PFK, but due to limitation in sqlite,
        # only is a FK
        # https://groups.google.com/forum/#!topic/sqlalchemy/TxISzgW7xUg
        # primary_key=True
    )
    file = relationship(
        "File",
        backref=backref('files_web')
    )
    name = Column(
        String(length=255),
        nullable=False,
        name='name'
    )
    # Many to one FileWeb <-> Scan
    id_scan = Column(
        Integer,
        ForeignKey('{0}scan.id'.format(tables_prefix)),
        nullable=False
    )
    scan = relationship(
        "Scan",
        backref=backref('files_web')
    )
    # insure there are no dup scan_file_idx
    __table_args__ = (UniqueConstraint('id_scan', 'scan_file_idx'),)

    def __init__(self, file, name, scan, idx):
        super(FileWeb, self).__init__()
        self.file = file
        self.name = name
        self.scan = scan
        self.scan_file_idx = idx

    @property
    def probes_total(self):
        return len(self.probe_results)

    @property
    def probes_finished(self):
        finished = 0
        for pr in self.probe_results:
            if pr.nosql_id is not None:
                finished += 1
        return finished

    @property
    def status(self):
        for pr in self.probe_results:
            if pr.nosql_id is not None:
                probe_result = ProbeRealResult(id=pr.nosql_id)
                if probe_result.type == IrmaProbeType.antivirus and \
                   probe_result.status == 1:
                    return 1
        return 0

    def get_probe_results(self, formatted=True):
        results = []

        for pr in self.probe_results:
            if pr.nosql_id is not None:
                probe_result = ProbeRealResult(id=pr.nosql_id)
                results.append(probe_result.to_json(formatted))

        return results

    @classmethod
    def query_find_by_name(cls, name, session):
        query = session.query(FileWeb)\
            .distinct(FileWeb.name)\
            .join(File)\
            .filter(FileWeb.name.like("%{0}%".format(name)))

        return query

    @classmethod
    def query_find_by_hash(cls, hash_type, hash_value, session):
        query = session.query(FileWeb)\
            .distinct(FileWeb.name)\
            .join(File)

        query = query.filter(getattr(File, hash_type) == hash_value)

        return query


class FileAgent(Base, SQLDatabaseObject):
    __tablename__ = '{0}fileAgent'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    submission_path = Column(
        String(length=255),
        nullable=False,
        name='submission_path'
    )
    # Many to one FileAgent <-> File as part of the primary key
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)),
        nullable=False,
        # conceptually it should be a PFK, but due to limitation in sqlite,
        # only is a FK
        # https://groups.google.com/forum/#!topic/sqlalchemy/TxISzgW7xUg
        # primary_key=True
    )
    file = relationship(
        "File",
        backref=backref('files_agent')
    )
    # Many to one FileAgent <-> Submission
    id_s = Column(
        Integer,
        ForeignKey('{0}submission.id'.format(tables_prefix)),
        nullable=False
    )
    submission = relationship(
        "Submission",
        backref=backref('files_agent')
    )

    def __init__(self, file, submission_path, submission):
        super(FileAgent, self).__init__()

        self.file = file
        self.submission_path = submission_path
        self.submission = submission


class Submission(Base, SQLDatabaseObject):
    __tablename__ = '{0}submission'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    external_id = Column(
        String(length=36),
        index=True,
        nullable=False,
        name='external_id'
    )
    os_name = Column(
        String,
        nullable=False,
        name='os_name'
    )
    username = Column(
        String,
        nullable=False,
        name='username'
    )
    ip = Column(
        String,
        nullable=False,
        name='ip'
    )
    date = Column(
        Integer,
        nullable=False,
        name='date'
    )

    def __init__(self, os_name, username, ip, date):
        super(Submission, self).__init__()

        self.external_id = UUID.generate()
        self.os_name = os_name
        self.username = username
        self.ip = ip
        self.date = date

    @classmethod
    def load_from_ext_id(cls, external_id, session):
        """Find the object in the database
        :param external_id: the id to look for
        :param session: the session to use
        :rtype: cls
        :return: the object that corresponds to the external_id
        :raise IrmaDatabaseResultNotFound, IrmaDatabaseError
        """
        try:
            return session.query(cls).filter(
                cls.external_id == external_id
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)


class ScanEvents(Base, SQLDatabaseObject):
    __tablename__ = '{0}scanEvents'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.get_sql_db_uri_params()[0] == 'sqlite':
        __table_args__ = {'sqlite_autoincrement': True}

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    status = Column(
        Integer,
        nullable=False,
        name='status'
    )
    timestamp = Column(
        Numeric(asdecimal=False),
        nullable=False,
        name='timestamp'
    )
    # Many to one FileWeb <-> Scan
    id_scan = Column(
        Integer,
        ForeignKey('{0}scan.id'.format(tables_prefix)),
        index=True,
        nullable=False
    )
    scan = relationship(
        "Scan",
        backref=backref('events')
    )

    def __init__(self, status, scan):
        super(ScanEvents, self).__init__()
        self.status = status
        self.timestamp = compat.timestamp()
        self.scan = scan
