import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Column = sqlalchemy.Column
Integer = sqlalchemy.Integer
Boolean = sqlalchemy.Boolean
String = sqlalchemy.String
DateTime = sqlalchemy.DateTime
Base = declarative_base()
ForeignKey = sqlalchemy.ForeignKey

class SQLDatabaseObject(object):
    pass