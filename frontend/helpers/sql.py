from contextlib import contextmanager
from frontend.models.sqlobjects import sql_db_connect
from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.common.exceptions import IrmaDatabaseError


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
