#
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

from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import config.parser as config
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.database.sqlobjects import SQLDatabaseObject


uri_params = config.get_sql_db_uri_params()
# TODO args* style argument
SQLDatabase.connect(uri_params[0], uri_params[1], uri_params[2],
                    uri_params[3], uri_params[4], uri_params[5])

Base = declarative_base()

tables_prefix = '{0}_'.format(config.get_sql_db_tables_prefix())


# Many to many Tag <-> File
tag_file = Table(
    '{0}tagFile'.format(tables_prefix),
    Base.metadata,
    Column(
        'id_tag',
        Integer,
        ForeignKey('{0}tag.id_tag'.format(tables_prefix))
    ),
    Column(
        'id_file',
        Integer,
        ForeignKey('{0}file.id_file'.format(tables_prefix)))
)


class Tag(Base, SQLDatabaseObject):
    __tablename__ = '{0}tag'.format(tables_prefix)

    _fields_suffix = '_tag'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    name = Column(
        String,
        nullable=False,
        name='name{0}'.format(_fields_suffix)
    )

    def __init__(self, name=''):
        super(Tag, self).__init__()

        self.name = name


class File(Base, SQLDatabaseObject):
    __tablename__ = '{0}file'.format(tables_prefix)

    _fields_suffix = '_file'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    sha256 = Column(
        String(length=64),
        name='sha256{0}'.format(_fields_suffix)
    )
    sha1 = Column(
        String(length=40),
        name='sha1{0}'.format(_fields_suffix)
    )
    md5 = Column(
        String(length=32),
        name='md5{0}'.format(_fields_suffix)
    )
    timestamp_first_scan = Column(
        String,
        nullable=False,
        name='timestamp_first_scan{0}'.format(_fields_suffix)
    )
    timestamp_last_scan = Column(
        String,
        nullable=False,
        name='timestamp_last_scan{0}'.format(_fields_suffix)
    )
    size = Column(
        Integer,
        name='size{0}'.format(_fields_suffix)
    )
    path = Column(
        String(length=255),
        name='path{0}'.format(_fields_suffix)
    )
    # Many to many Tag <-> File
    tags = relationship(
        'Tag',
        secondary=tag_file,
        backref='files'
    )

    def __init__(self, timestamp_first_scan, timestamp_last_scan,
                 sha256=None, sha1=None, md5=None, size=None,
                 path=None, tags=[]):
        super(File, self).__init__()

        self.timestamp_first_scan = timestamp_first_scan
        self.timestamp_last_scan = timestamp_last_scan
        self.sha256 = sha256
        self.sha1 = sha1
        self.md5 = md5
        self.size = size
        self.path = path
        self.tags = tags


class ScanResult(Base, SQLDatabaseObject):
    __tablename__ = '{0}scanResult'.format(tables_prefix)

    _fields_suffix = '_sr'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    probe_type = Column(
        String,
        nullable=False,
        name='probe_type{0}'.format(_fields_suffix)
    )
    probe_code = Column(
        String,
        nullable=False,
        name='probe_code{0}'.format(_fields_suffix)
    )
    no_sql_id = Column(
        String,
        nullable=False,
        name='no_sql_id{0}'.format(_fields_suffix)
    )
    state = Column(
        String,
        nullable=False,
        name='state{0}'.format(_fields_suffix)
    )
    # Many to one ScanResult <-> File
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id_file'.format(tables_prefix))
    )
    file = relationship(
        "File",
        backref=backref('scan_results')
    )

    def __init__(self, probe_type, probe_code, no_sql_id, state, file=None):
        super(ScanResult, self).__init__()

        self.probe_type = probe_type
        self.probe_code = probe_code
        self.no_sql_id = no_sql_id
        self.state = state
        self.file = file


class Scan(Base, SQLDatabaseObject):
    __tablename__ = '{0}scan'.format(tables_prefix)

    _fields_suffix = '_scan'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    status = Column(
        String,
        nullable=False,
        name='status{0}'.format(_fields_suffix)
    )
    date = Column(
        Integer,
        nullable=False,
        name='date{0}'.format(_fields_suffix)
    )
    ip = Column(
        String,
        nullable=False,
        name='ip{0}'.format(_fields_suffix)
    )

    def __init__(self, status, date, ip):
        super(Scan, self).__init__()

        self.status = status
        self.date = date
        self.ip = ip


class FileWeb(Base, SQLDatabaseObject):
    __tablename__ = '{0}fileWeb'.format(tables_prefix)

    _fields_suffix = '_fw'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    # Many to one FileWeb <-> File as part of the primary key
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id_file'.format(tables_prefix)),
        nullable=False,
        primary_key=True
    )
    file = relationship(
        "File",
        backref=backref('files_web')
    )
    name = Column(
        String(length=255),
        nullable=False,
        name='name{0}'.format(_fields_suffix)
    )
    # Many to one FileWeb <-> Scan
    id_scan = Column(
        Integer,
        ForeignKey('{0}scan.id_scan'.format(tables_prefix)),
        nullable=False
    )
    scan = relationship(
        "Scan",
        backref=backref('files_web')
    )

    def __init__(self, file, name, scan):
        super(FileWeb, self).__init__()

        self.file = file
        self.name = name
        self.scan = scan


class FileAgent(Base, SQLDatabaseObject):
    __tablename__ = '{0}fileAgent'.format(tables_prefix)

    _fields_suffix = '_fa'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    submission_path = Column(
        String(length=255),
        nullable=False,
        name='submission_path{0}'.format(_fields_suffix)
    )
    # Many to one FileAgent <-> File as part of the primary key
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id_file'.format(tables_prefix)),
        nullable=False,
        primary_key=True
    )
    file = relationship(
        "File",
        backref=backref('files_agent')
    )
    # Many to one FileAgent <-> Submission
    id_s = Column(
        Integer,
        ForeignKey('{0}submission.id_s'.format(tables_prefix)),
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

    _fields_suffix = '_s'
    _idname = 'id{0}'.format(_fields_suffix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name=_idname
    )
    os_name = Column(
        String,
        nullable=False,
        name='os_name{0}'.format(_fields_suffix)
    )
    username = Column(
        String,
        nullable=False,
        name='username{0}'.format(_fields_suffix)
    )
    ip = Column(
        String,
        nullable=False,
        name='ip{0}'.format(_fields_suffix)
    )
    date = Column(
        Integer,
        nullable=False,
        name='date{0}'.format(_fields_suffix)
    )

    def __init__(self, os_name, username, ip, date):
        super(Submission, self).__init__()

        self.os_name = os_name
        self.username = username
        self.ip = ip
        self.date = date

Base.metadata.create_all(SQLDatabase.get_engine())
