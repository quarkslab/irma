import sys

from brain.models.sqlobjects import User
from brain.helpers.sql import session_transaction

from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


if len(sys.argv) not in (4, 5):
    print("usage: {0} <username> <rmqvhost> <ftpuser> [quota]\n"
          "      with <username> a string\n"
          "           <rmqvhost> the rmqvhost used for the frontend\n"
          "           <ftpuser> the ftpuser used by the frontend\n"
          "           [quota] the number of file scan quota\n"
          "example: {0} test1 mqfrontend frontend"
          "".format(sys.argv[0]))
    sys.exit(1)

name = sys.argv[1]
rmqvhost = sys.argv[2]
ftpuser = sys.argv[3]
# quota is in number of files (0 means disabled)
quota = int(sys.argv[4]) if len(sys.argv) == 5 else 0
with session_transaction() as session:
    try:
        user = User.get_by_rmqvhost(rmqvhost, session)
        print("rmqvhost {0} is already assigned to user {1}. "
              "Updating with new parameters.".format(user.name, user.rmqvhost))
        user = user.load(user.id, session)
        user.name = name
        user.ftpuser = ftpuser
        user.quota = quota
        user.update(['name', 'ftpuser', 'quota'], session)
    except IrmaDatabaseResultNotFound:
        user = User(name=name, rmqvhost=rmqvhost, ftpuser=ftpuser, quota=quota)
        user.save(session)
