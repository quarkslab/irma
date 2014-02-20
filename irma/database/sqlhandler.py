import logging, sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

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

    def one_by(self, classname, **kwargs):
        try:
            return self._session.query(classname).filter_by(**kwargs).one()
        except NoResultFound:
            raise IrmaDatabaseError("No result found instead of one")
        except MultipleResultsFound:
            raise IrmaDatabaseError("Multiple results found instead of one")

    def one(self, classname, filter_expr):
        try:
            return self._session.query(classname).filter_by(filter_expr).one()
        except NoResultFound:
            raise IrmaDatabaseError("No result found instead of one")
        except MultipleResultsFound:
            raise IrmaDatabaseError("Multiple results found instead of one")

    def find_by(self, classname, **kwargs):
        return self._session.query(classname).filter_by(**kwargs).all()

    def find(self, classname, filter_expr):
        return self._session.query(classname).filter(filter_expr).all()

    def count(self, classname):
        return self._session.query(classname).count()

    def delete(self, obj):
        return self._session.delete(obj)

    def _sum(self, elts):
        res = 0
        for e in elts:
            res += e[0]
        return res

    def sum_by(self, field, **kwargs):
        t = self.find_by(field, **kwargs)
        return self._sum(t)

    def sum(self, field, filter_expr):
        t = self.find(field, filter_expr)
        return self._sum(t)
