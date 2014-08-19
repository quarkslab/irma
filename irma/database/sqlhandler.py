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

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from irma.common.exceptions import IrmaDatabaseError

DEBUG = False
logging.basicConfig(filename='/var/log/irma/sqlalchemy.log')
if DEBUG:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
else:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


class SQLDatabase(object):
    """Internal database.
    This class handles the creation of the internal database.
    """

    __engine = None
    __Session = None

    def __init__(self):
        raise Exception('This class must not be instantiated')

    @classmethod
    def connect(cls, dbms, dialect, username, passwd, host, dbname):
        """Create a connexion to the db
        :param dbms: the database management system (ex: postgresql)
        :param dialect: the dialect to use (ex: psycopg2 (for postgre))
        :param username: the username for the connexion
        :param passwd: the password for the connexion
        :param host: the host (ex: localhost or localhost:port)
        :param dbname: the name of the database (has to exist)
        """
        if cls.__engine is None:
            if dialect:
                dbms = "{0}+{1}".format(dbms, dialect)
            host_and_id = ''
            if host and username:
                if passwd:
                    host_and_id = "{0}:{1}@{2}".format(username, passwd, host)
                else:
                    host_and_id = "{0}@{1}".format(username, host)
            url = "{0}://{1}/{2}".format(dbms, host_and_id, dbname)
            cls.__engine = create_engine(url, echo=False)

            session_factory = sessionmaker(bind=cls.__engine)
            cls.__Session = scoped_session(session_factory)
            logging.info('engine connected')
        else:
            logging.info('engine already connected, nothing to do')

    @classmethod
    def get_engine(cls):
        """Return the engine
        :rtype: engine
        :raise IrmaDatabaseError: if the engine is None
        """
        if cls.__engine is None:
            raise IrmaDatabaseError('the engine has to be connected first')
        return cls.__engine

    @classmethod
    def get_session(cls):
        """Return a session
        :rtype: scoped_session
        :raise IrmaDatabaseError: if the engine is None
        """
        if cls.__engine is None:
            raise IrmaDatabaseError('the engine has to be connected first')
        return cls.__Session()
