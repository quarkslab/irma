import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Column = sqlalchemy.Column
Integer = sqlalchemy.Integer
String = sqlalchemy.String
DateTime = sqlalchemy.DateTime
Base = declarative_base()

class SQLDatabaseObject(object):
    pass