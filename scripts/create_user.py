import sys
from brain.models.sqlobjects import User
from brain.helpers.sql import session_transaction


if len(sys.argv) not in (4, 5):
    print("usage: {0} <username> <rmqvhost> <ftpuser> [quota]\n"
          "      with <username> a string\n"
          "           <rmqvhost> the rmqvhost used for the frontend\n"
          "           <ftpuser> the ftpuser used by the frontend\n"
          "           [quota] the number of file scan quota\n"
          "example: {0} test1 mqfrontend frontend"
          "".format(sys.argv[0]))
    sys.exit(1)

# quota is in number of files (0 means disabled)
quota = int(sys.argv[4]) if len(sys.argv) == 5 else 0
with session_transaction() as session:
    user = User(name=sys.argv[1],
                rmqvhost=sys.argv[2],
                ftpuser=sys.argv[3],
                quota=quota)
    user.save(session)
