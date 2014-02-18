import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Column = sqlalchemy.Column
Integer = sqlalchemy.Integer
String = sqlalchemy.String
Base = declarative_base()

class SQLDatabaseObject(object):
    pass