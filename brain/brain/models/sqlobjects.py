#
# Copyright (c) 2013-2018 Quarkslab.
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

from sqlalchemy import Column, Integer, Float, String, \
    event, ForeignKey, Boolean
import config.parser as config
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from irma.common.utils.utils import UUID
from irma.common.base.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound
from irma.common.base.utils import IrmaScanStatus
from irma.common.utils.compat import timestamp


# SQLite fix for ForeignKey support
# see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
if config.sqldb.dbms == 'sqlite':
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection,
                          connection_record):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

Base = declarative_base()
tables_prefix = '{0}_'.format(config.sqldb.tables_prefix)


class Scan(Base):
    __tablename__ = '{0}scan'.format(tables_prefix)
    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.sqldb.dbms == 'sqlite':
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
    # Many to one Scan <-> User
    user_id = Column(
        Integer,
        ForeignKey('{0}user.id'.format(tables_prefix)),
        index=True,
        nullable=False,
    )
    jobs = relationship("Job", backref="scan", lazy='subquery')

    def __init__(self, frontend_scanid, user_id):
        self.scan_id = frontend_scanid
        self.status = IrmaScanStatus.empty
        self.timestamp = timestamp()
        self.user_id = user_id

    @property
    def files(self):
        return set(job.filename for job in self.jobs)

    @property
    def nb_files(self):
        return len(self.files)

    @classmethod
    def get_scan(cls, scan_id, user_id, session):
        try:
            return session.query(cls).filter(
                cls.scan_id == scan_id and cls.user_id == user_id
                ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)


class User(Base):
    __tablename__ = '{0}user'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.sqldb.dbms == 'sqlite':
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
    scans = relationship("Scan", backref="user")

    def __init__(self, name, rmqvhost, ftpuser):
        self.name = name
        self.rmqvhost = rmqvhost
        self.ftpuser = ftpuser

    @staticmethod
    def get_by_rmqvhost(session, rmqvhost=None):
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


class Job(Base):
    __tablename__ = '{0}job'.format(tables_prefix)

    # Fields
    task_id = Column(
        String,
        name="task_id",
        primary_key=True,
    )
    # Many to one Job <-> Scan
    scan_id = Column(
        Integer,
        ForeignKey('{0}scan.id'.format(tables_prefix)),
        index=True,
        nullable=False,
    )
    filename = Column(
        String,
        nullable=False,
        name='filename'
    )
    probename = Column(
        String,
        nullable=False,
        name='probename'
    )

    def __init__(self, scanid, filename, probename):
        self.task_id = UUID.generate()
        self.scan_id = scanid
        self.filename = filename
        self.probename = probename


class Probe(Base):
    __tablename__ = '{0}probe'.format(tables_prefix)

    # SQLite fix for auto increment on ids
    # see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    if config.sqldb.dbms == 'sqlite':
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
    display_name = Column(
        String,
        nullable=False,
        index=True,
        name='display_name'
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

    def __init__(self, name, display_name, category, mimetype_regexp, online):
        self.name = name
        self.display_name = display_name
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
