import sys
import os

import config.parser as config
from brain.helpers.sql import session_transaction
from brain.models.sqlobjects import User, Base
from sqlalchemy import create_engine

from irma.common.base.exceptions import IrmaDatabaseResultNotFound,\
    IrmaDatabaseError


if len(sys.argv) not in (4, 5):
    print("usage: {0} <username> <rmqvhost> <ftpuser>\n"
          "      with <username> a string\n"
          "           <rmqvhost> the rmqvhost used for the frontend\n"
          "           <ftpuser> the ftpuser used by the frontend\n"
          "example: {0} test1 mqfrontend frontend"
          "".format(sys.argv[0]))
    sys.exit(1)

name = sys.argv[1]
rmqvhost = sys.argv[2]
ftpuser = sys.argv[3]

# Auto-create directory for sqlite db
db_name = os.path.abspath(config.sqldb.dbname)
dirname = os.path.dirname(db_name)
if not os.path.exists(dirname):
    print("SQL directory does not exist {0}"
          "..creating".format(dirname))
    os.makedirs(dirname)
    os.chmod(dirname, 0o777)
elif not (os.path.isdir(dirname)):
    print("Error. SQL directory is a not a dir {0}"
          "".format(dirname))
    raise IrmaDatabaseError("Can not create Brain database dir")

if not os.path.exists(db_name):
    # touch like method to create a rw-rw-rw- file for db
    open(db_name, 'a').close()
    os.chmod(db_name, 0o666)

# Retrieve database informations
engine = create_engine(config.sqldb.url, echo=config.sql_debug_enabled())
# and create Database in case
Base.metadata.create_all(engine)

with session_transaction() as session:
    try:
        user = User.get_by_rmqvhost(session, rmqvhost=rmqvhost)
        print("rmqvhost {0} is already assigned to user {1}. "
              "Updating with new parameters.".format(user.name, user.rmqvhost))
        session.query(User)\
            .filter_by(id=user.id)\
            .update({'name': name, 'ftpuser': ftpuser})
    except IrmaDatabaseResultNotFound:
        user = User(name=name, rmqvhost=rmqvhost, ftpuser=ftpuser)
        session.add(user)
