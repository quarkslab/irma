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
from brain.helpers.sql import sql_db_connect
from sqlalchemy import Column, Integer, Float, String, \
    event, ForeignKey, Boolean
import config.parser as config
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound
from lib.irma.common.utils import IrmaScanStatus
from lib.common.compat import timestamp
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.database.sqlobjects import SQLDatabaseObject


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


sql_db_connect()
Base = declarative_base()
tables_prefix = '{0}_'.format(config.get_sql_db_tables_prefix())


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
    scan_id = Column(
        String,
        index=True,
        nullable=False,
        name='scan_id'
    )
    status = Column(
        Integer,
        nullable=False,
        name='status'
    )
    timestamp = Column(
        Float(precision=2),
        nullable=False,
        name='timestamp'
    )
    nb_files = Column(
        Integer,
        nullable=False,
        name='nb_files'
    )
    # Many to one Scan <-> User
    user_id = Column(
        Integer,
        ForeignKey('{0}user.id'.format(tables_prefix)),
        index=True,
        nullable=False,
    )
    jobs = relationship("Job", backref="scan", lazy='subquery')

    def __init__(self, frontend_scanid, user_id, nb_files):
        self.scan_id = frontend_scanid
        self.status = IrmaScanStatus.empty
        self.timestamp = timestamp()
        self.nb_files = nb_files
        self.user_id = user_id

    @staticmethod
    def get_scan(scan_id, user_id, session):
        try:
            return session.query(Scan).filter(
                Scan.scan_id == scan_id and Scan.user_id == user_id
                ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    @property
    def nb_jobs(self):
        return len(self.jobs)

    def progress(self):
        finished = success = total = 0
        for job in self.jobs:
            total += 1
            if job.finished():
                finished += 1
                if job.status == Job.success:
                    success += 1
        return (total, finished, success)

    def get_pending_jobs_taskid(self):
        pending_jobs_taskid = []
        for job in self.jobs:
            if not job.finished():
                pending_jobs_taskid.append(job.task_id)
        return pending_jobs_taskid

    def finished(self):
        for job in self.jobs:
            if not job.finished():
                return False
        return True


class User(Base, SQLDatabaseObject):
    __tablename__ = '{0}user'.format(tables_prefix)

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
    rmqvhost = Column(
        String,
        index=True,
        nullable=False,
        name='rmqvhost'
    )
    ftpuser = Column(
        String,
        nullable=False,
        name='ftpuser'
    )
    quota = Column(
        Integer,
        name='quota'
    )
    scans = relationship("Scan", backref="user")

    def __init__(self, name, rmqvhost, ftpuser, quota):
        self.name = name
        self.rmqvhost = rmqvhost
        self.ftpuser = ftpuser
        self.quota = quota

    @staticmethod
    def get_by_rmqvhost(rmqvhost, session):
        # FIXME: get rmq_vhost dynamically
        if rmqvhost is None:
            rmqvhost = config.brain_config['broker_frontend'].vhost
        try:
            return session.query(User).filter(
                User.rmqvhost == rmqvhost
                ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    def remaining_quota(self, session):
        if self.quota == 0:
            # quota=0 means quota disabled
            remaining = None
        else:
            # quota are per 24h
            min_ts = timestamp() - 24 * 60 * 60
            scan_list = session.query(Scan).filter(
                Scan.user_id == self.id).filter(
                Scan.timestamp >= min_ts).all()
            consumed = 0
            for scan in scan_list:
                consumed += scan.nb_jobs
            # Quota are set per 24 hours
            remaining = self.quota - consumed
        return remaining


class Job(Base, SQLDatabaseObject):
    __tablename__ = '{0}job'.format(tables_prefix)
    success = 1
    running = 0
    error = -1

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
    filename = Column(
        String,
        nullable=False,
        index=True,
        name='filename'
    )
    probename = Column(
        String,
        nullable=False,
        index=True,
        name='probename'
    )
    status = Column(
        Integer,
        nullable=False,
        name='status'
    )
    ts_start = Column(
        Integer,
        nullable=False,
        name='ts_start'
    )
    ts_end = Column(
        Integer,
        name='ts_end'
    )
    task_id = Column(
        String,
        name="task_id"
    )
    # Many to one Job <-> Scan
    scan_id = Column(
        Integer,
        ForeignKey('{0}scan.id'.format(tables_prefix)),
        index=True,
        nullable=False,
    )

    def __init__(self, filename, probename, scanid, taskid):
        self.filename = filename
        self.probename = probename
        self.ts_start = timestamp()
        self.status = self.running
        self.scan_id = scanid
        self.task_id = taskid

    def finished(self):
        return self.status != self.running


class Probe(Base, SQLDatabaseObject):
    __tablename__ = '{0}probe'.format(tables_prefix)

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
        index=True,
        name='name'
    )
    category = Column(
        String,
        nullable=False,
        name='category'
    )
    mimetype_regexp = Column(
        String,
        name='mimetype_regexp'
    )
    online = Column(
        Boolean,
        name='online'
    )

    def __init__(self, name, category, mimetype_regexp, online):
        self.name = name
        self.category = category
        self.mimetype_regexp = mimetype_regexp
        self.online = online

    @classmethod
    def get_by_name(cls, name, session):
        try:
            return session.query(cls).filter(
                Probe.name == name
                ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    @classmethod
    def all(cls, session):
        return session.query(cls).all()


Base.metadata.create_all(SQLDatabase.get_engine())
