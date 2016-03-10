import logging
from contextlib import contextmanager
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.common.exceptions import IrmaDatabaseError
import config.parser as config

log = logging.getLogger(__name__)


def sql_db_connect():
    """Connection to DB
    """
    try:
        uri_params = config.get_sql_db_uri_params()
        # TODO args* style argument
        SQLDatabase.connect(uri_params[0], uri_params[1], uri_params[2],
                            uri_params[3], uri_params[4], uri_params[5],
                            debug=config.debug_enabled())
    except Exception as e:
        log.exception(e)
        msg = "SQL: can't connect"
        raise IrmaDatabaseError(msg)


@contextmanager
def session_transaction():
    """Provide a transactional scope around a series of operations."""
    # TODO: when used with 'with', session is not commited and usage of vars
    #       such as object.id could not be initialized (None)
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
