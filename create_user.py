import sys
from cryptacular.bcrypt import BCRYPTPasswordManager
from xonstat_queue import *

def main(argv=None):
    if len(argv) != 3:
        print "Usage: create_user.py <username> <password>"
        sys.exit(1)

    session = dbsession()
    username = argv[1]
    password = argv[2]
    manager = BCRYPTPasswordManager()
    hashed_password = manager.encode(password)

    user = User()
    user.username = username
    user.password = hashed_password
    user.active_ind = True

    try:
        session.add(user)
        session.commit()
        print "User {0} created.".format(username)
    except:
        print "Error adding user."
        session.rollback()
        session.close()
        sys.exit(1)

    session.close()
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
