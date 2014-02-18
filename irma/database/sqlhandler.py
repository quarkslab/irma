import logging, sqlalchemy
from sqlalchemy.orm import sessionmaker

from irma.common.exceptions import IrmaDatabaseError

log = logging.getLogger(__name__)

class SQLDatabase(object):
    """Internal database.

    This class handles the creation of the internal database and provides some
    functions for interacting with it.
    """

    ##########################################################################
    # Constructor and Destructor stuff
    ##########################################################################
    def __init__(self, engine):
        self._db = sqlalchemy.create_engine(engine)
        self._db.echo = False
        self._session = None
        self._connect()

    def __del__(self):
        if self._session:
            self._session.commit()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.__del__()

    ##########################################################################
    # Private methods
    ##########################################################################

    def _connect(self):
        Session = sessionmaker(bind=self._db)
        self._session = Session()

    def _disconnect(self):
        if not self._session:
            return
        try:
            self._session.commit()
            self._session.close()
        except Exception as e:
            self._session.rollback()
            raise IrmaDatabaseError("{0}".format(e))

    ##########################################################################
    # Public methods
    ##########################################################################
    def add(self, entry):
        self._session.add(entry)

    def add_all(self, entries):
        self._session.add_all(entries)

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    def all(self, classname):
        return self._session.query(classname).all()

    def find(self, classname, **kwargs):
        return self._session.query(classname).filter_by(**kwargs).all()

    def count(self, classname):
        return self._session.query(classname).count()

    def delete(self, obj):
        return self._session.delete(obj)
