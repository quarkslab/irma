#
# Copyright (c) 2013-2014 QuarksLab.
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
from sqlalchemy import Column, Integer, String, \
    event, ForeignKey
import config.parser as config
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from lib.irma.common.exceptions import IrmaDatabaseError, \
    IrmaDatabaseResultNotFound
from lib.irma.common.utils import IrmaScanStatus
from lib.common.compat import timestamp
from lib.irma.database.sqlobjects import SQLDatabaseObject


# SQLite fix for ForeignKey support
# see http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Auto-create directory for sqlite db
db_name = config.brain_config['sql_brain'].dbname
dirname = os.path.dirname(db_name)
dirname = os.path.abspath(dirname)
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


class Scan(Base, SQLDatabaseObject):
    __tablename__ = 'Scan'
    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    timestamp = Column(
        String,
        nullable=False,
        name='timestamp'
    )
    scanid = Column(
        String,
        index=True,
        nullable=False,
        name='scanid'
    )
    nbfiles = Column(
        Integer,
        name='nbfiles'
    )
    # Many to one Scan <-> User
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable=False,
        name="user_id"
    )
    user = relationship("User")

    def __repr__(self):
        str_repr = (
            "Scan {0}:".format(self.scanid) +
            "\tdate: {0}".format(self.timestamp) +
            "\t{0} file(s)".format(self.nbfiles) +
            "\tstatus: '{0}'".format(IrmaScanStatus.label[self.status]) +
            "\tuser_id: {0}\n".format(self.user_id))
        return str_repr

    @staticmethod
    def get_scan(scanid, user_id, session):
        try:
            return session.query(User).filter(
                Scan.scanid == scanid and Scan.user_id == user_id
                ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)


class User(Base, SQLDatabaseObject):
    __tablename__ = 'User'

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

    def __repr__(self):
        str_repr = (
            "User {0}:".format(self.name) +
            "\trmq_vhost: '{0}'".format(self.rmqvhost) +
            "\t ftpuser: '{0}'".format(self.ftpuser) +
            "\tquota: '{0}'\n".format(self.quota))
        return str_repr

    @staticmethod
    def get_by_rmqvhost(rmqvhost, session):
        # FIXME: get rmq_vhost dynamically
        if rmqvhost is None:
            rmqvhost = config.brain_config['broker_frontend'].vhost
        try:
            return session.query(User).filter(
                User.rmq_vhost == rmqvhost
                ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    def remaining_quota(self, session):
        if self.quota == 0:
            # quota=0 means quota disabled
            quota = None
        else:
            # quota are per 24h
            min_date = timestamp() - 24 * 60 * 60
            files_consumed = session.query(Scan.nb_files).filter(
                Scan.date >= min_date and Scan.user_id == self.id
                ).all()
            # Quota are set per 24 hours
            quota = self.quota - sum(files_consumed)
        return quota
