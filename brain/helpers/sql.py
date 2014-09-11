import logging
from contextlib import contextmanager
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.common.exceptions import IrmaDatabaseError
import config.parser as config

log = logging.getLogger(__name__)


def sql_db_connect():
    try:
        engine = config.brain_config['sql_brain'].engine
        dbname = config.brain_config['sql_brain'].dbname
        SQLDatabase.connect(engine, None, None, None, None, dbname)
    except Exception as e:
        msg = "SQL: can't connect"
        log.debug(msg + " [{0}]".format(e))
        raise IrmaDatabaseError(msg)


@contextmanager
def session_transaction():
    """Provide a transactional scope around a series of operations."""
    sql_db_connect()
    session = SQLDatabase.get_session()
    try:
        yield session
        session.commit()
    except IrmaDatabaseError:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_query():
    """Provide a transactional scope around a series of operations."""
    sql_db_connect()
    session = SQLDatabase.get_session()
    try:
        yield session
    except IrmaDatabaseError:
        raise
