from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from irma.common.utils import sql
import config.parser as config


engine = create_engine(config.sqldb.url, echo=config.sql_debug_enabled())
session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                      bind=engine))


def session_transaction():
    return sql.transaction(session)


def session_query():
    return sql.query(session)
