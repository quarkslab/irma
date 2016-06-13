#
# Copyright (c) 2013-2016 Quarkslab.
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

import os

from sqlalchemy import Table, Column, Integer, Numeric, Boolean, ForeignKey, \
    String, UniqueConstraint, and_
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import func

import config.parser as config
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaCoreError, IrmaFileSystemError
from lib.common import compat
from lib.common.utils import UUID
from lib.irma.common.utils import IrmaScanStatus, IrmaProbeType
from lib.irma.database.sqlobjects import SQLDatabaseObject
from frontend.helpers.format import IrmaFormatter


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

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    text = Column(
        String,
        nullable=False,
        name='text'
    )

    # Many to many Tag <-> File
    files = relationship(
        'File',
        secondary=tag_file,
        backref='tags',
        lazy='dynamic',
    )

    def __init__(self, text=''):
        super(Tag, self).__init__()
        self.text = text

    def to_json(self):
        return dict((k, v) for (k, v) in self.to_dict().items())

    @classmethod
    def query_find_all(cls, session):
        return session.query(Tag).all()


class File(Base, SQLDatabaseObject):
    __tablename__ = '{0}file'.format(tables_prefix)

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
    mimetype = Column(
        String,
        name='mimetype'
    )
    path = Column(
        String(length=255),
        name='path'
    )

    def __init__(self, sha256, sha1, md5, size, mimetype, path,
                 timestamp_first_scan, timestamp_last_scan, tags=[]):
        super(File, self).__init__()

        self.sha256 = sha256
        self.sha1 = sha1
        self.md5 = md5
        self.size = size
        self.mimetype = mimetype
        self.path = path
        self.timestamp_first_scan = timestamp_first_scan
        self.timestamp_last_scan = timestamp_last_scan
        self.tags = tags

    def add_tag(self, tagid, session):
        asked_tag = Tag.find_by_id(tagid, session)
        if asked_tag in self.tags:
            raise IrmaDatabaseError("Adding an already present Tag")
        self.tags.append(asked_tag)

    def remove_tag(self, tagid, session):
        asked_tag = Tag.find_by_id(tagid, session)
        if asked_tag not in self.tags:
            raise IrmaDatabaseError("Removing a not present Tag")
        self.tags.remove(asked_tag)

    def to_json(self):
        # return only these keys
        keys = ["md5", "sha1", "sha256", "size",
                "timestamp_first_scan", "timestamp_last_scan"]
        return dict((k, v) for (k, v) in self.to_dict().items() if k in keys)

    @classmethod
    def load_from_sha256(cls, sha256, session):
        """Find the object in the database, update data if file was previously deleted
        :param sha256: the sha256 to look for
        :param session: the session to use
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
        # Check if file is still present
        if asked_file.path is not None and not os.path.exists(asked_file.path):
            asked_file.path = None
        return asked_file

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

    def get_tags(self, formatted=True):
        results = []
        for t in self.tags:
            results.append(t.to_json())
        return results

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
        return list(set(from_web))


class ProbeResult(Base, SQLDatabaseObject):
    __tablename__ = '{0}probeResult'.format(tables_prefix)

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
    doc = Column(
        JSONB,
        name='doc'
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
                 doc,
                 status,
                 file_web=None):
        super(ProbeResult, self).__init__()

        self.type = type
        self.name = name
        self.doc = doc
        self.status = status
        self.files_web = [file_web]

    def get_details(self, formatted=True):
        res = self.doc.copy()
        res.pop('uploaded_files', '')
        # apply or not IrmaFormatter
        if formatted:
            res = IrmaFormatter.format(self.name, res)
        return res


class Scan(Base, SQLDatabaseObject):
    __tablename__ = '{0}scan'.format(tables_prefix)

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
    probelist = Column(
        String,
        name='probelist'
    )
    force = Column(
        Boolean,
        name='force'
    )
    mimetype_filtering = Column(
        Boolean,
        name='mimetype_filtering'
    )
    resubmit_files = Column(
        Boolean,
        name='resubmit_files'
    )

    def get_probelist(self):
        return self.probelist.split(",")

    def set_probelist(self, value):
        self.probelist = ",".join(value)

    def __init__(self, date, ip):
        super(Scan, self).__init__()
        self.external_id = UUID.generate()
        self.date = date
        self.ip = ip
        self.force = False
        self.mimetype_filtering = False
        self.resubmit_files = False

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
        # Check min. status
        # It could happend that launched status
        # is not yet received and results are already
        # there so just check that we are at least at uploaded
        if self.status < IrmaScanStatus.uploaded:
            return False
        for fw in self.files_web:
            for pr in fw.probe_results:
                if pr.doc is None:
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

    @property
    def files(self):
        return list(set([fw.file for fw in self.files_web]))

    def set_status(self, status_code):
        if status_code not in IrmaScanStatus.label.keys():
            raise IrmaCoreError("Trying to update with an unknown status")
        if status_code not in [evt.status for evt in self.events]:
            evt = ScanEvents(status_code, self)
            self.events.append(evt)

    def get_filewebs_by_sha256(self, sha256):
        fws = []
        for file_web in self.files_web:
            if file_web.file.sha256 == sha256:
                fws.append(file_web)
        return fws

    @classmethod
    def query_find_by_filesha256(cls, hash_value, session,):
        query = session.query(Scan)
        query = query.join(FileWeb, FileWeb.id_scan == Scan.id)
        query = query.join(File, File.id == FileWeb.id_file)
        query = query.filter(File.sha256 == hash_value)
        return query


class FileWeb(Base, SQLDatabaseObject):
    __tablename__ = '{0}fileWeb'.format(tables_prefix)

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
    # Many to one FileWeb <-> File as part of the primary key
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)),
        nullable=False,
        # should be a PFK only a FK
        # https://groups.google.com/forum/#!topic/sqlalchemy/TxISzgW7xUg
        # primary_key=True
    )
    file = relationship(
        "File",
        backref=backref('files_web'),
        foreign_keys='FileWeb.id_file'
    )
    name = Column(
        String(length=255),
        nullable=False,
        name='name'
    )
    path = Column(
        String(length=255),
        name='path'
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
    # Many to one FileWeb <-> Scan
    id_parent = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)),
    )
    # Many to one FileWeb <-> File
    parent = relationship("File",
                          backref="children",
                          foreign_keys='FileWeb.id_parent')

    # insure there are no dup external_id
    __table_args__ = (UniqueConstraint('external_id'),)

    def __init__(self, file, name, path, scan):
        super(FileWeb, self).__init__()
        self.external_id = UUID.generate()
        self.file = file
        self.name = name
        self.path = path
        self.scan = scan

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

    @classmethod
    def load_by_scanid_fileid(cls, scanid, fileid, session):
        """Find the list of filewebs in a given scan with
           same file in the database
        :param scanid: the scan external id
        :param fileid: the file id
        :param session: the session to use
        :rtype: list of FileWeb
        :return: list of matching objects
        :raise: IrmaDatabaseResultNotFound
        """
        try:
            return session.query(cls).filter(
                cls.id_scan == scanid,
                cls.id_file == fileid
            ).all()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)

    @property
    def probes_total(self):
        return len(self.probe_results)

    @property
    def probes_finished(self):
        finished = 0
        for pr in self.probe_results:
            if pr.doc is not None:
                finished += 1
        return finished

    @property
    def status(self):
        for pr in self.probe_results:
            if pr.doc is not None:
                probe_result = pr.doc
                if probe_result['type'] == IrmaProbeType.antivirus and \
                   probe_result['status'] == 1:
                    return 1
        return 0

    def get_probe_results(self, formatted=True):
        results = []

        for pr in self.probe_results:
            if pr.doc is not None:
                results.append(pr.get_details(formatted))

        return results

    @classmethod
    def query_find_by_name(cls, name, tags, session):
        last_ids = session.query(FileWeb.id_file,
                                 FileWeb.name,
                                 func.max(FileWeb.id).label('last_id'))\
            .group_by(FileWeb.id_file, FileWeb.name).subquery()

        query = session.query(FileWeb)\
            .join((last_ids, and_(FileWeb.id_file == last_ids.c.id_file,
                                  FileWeb.name == last_ids.c.name,
                                  FileWeb.id == last_ids.c.last_id)))\
            .join(File, File.id == FileWeb.id_file)\
            .filter(FileWeb.name.like(u"%{0}%".format(name)))\
            .order_by(FileWeb.name)

        # Update the query with tags if user asked for it
        if tags is not None:
            query = query.join(File.tags)
            for tagid in tags:
                # check if tag exists
                Tag.find_by_id(tagid, session)
                query = query.filter(File.tags.any(Tag.id == tagid))

        return query

    @classmethod
    def query_find_by_hash(cls, hash_type, hash_value, tags, session,
                           distinct_name=True):
        if distinct_name:
            last_ids = session.query(FileWeb.id_file,
                                     FileWeb.name,
                                     func.max(FileWeb.id).label('last_id'))\
                .group_by(FileWeb.id_file, FileWeb.name).subquery()

            query = session.query(FileWeb)\
                .join((last_ids, and_(FileWeb.id_file == last_ids.c.id_file,
                                      FileWeb.name == last_ids.c.name,
                                      FileWeb.id == last_ids.c.last_id)))
        else:
            query = session.query(FileWeb)

        query = query.join(File, File.id == FileWeb.id_file)

        query = query.filter(getattr(File, hash_type) == hash_value)\
            .order_by(FileWeb.name)
        # Update the query with tags if user asked for it
        if tags is not None:
            query = query.join(File.tags)
            for tagid in tags:
                # check if tag exists
                Tag.find_by_id(tagid, session)
                query = query.filter(File.tags.any(Tag.id == tagid))

        return query


class ScanEvents(Base, SQLDatabaseObject):
    __tablename__ = '{0}scanEvents'.format(tables_prefix)

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
