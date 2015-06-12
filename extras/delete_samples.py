from lib.common.utils import humanize_time_str
from frontend.models.sqlobjects import File
from frontend.helpers.sessions import session_query
from lib.common import compat
import os


def clean_db(max_age=4 * 60 * 60):
    with session_query() as session:
        fl = session.query(File).filter(
            File.timestamp_last_scan < compat.timestamp() - max_age
        ).all()
        nb = 0
        for f in fl:
            print f
            if f.path is not None and os.path.exists(f.path):
                os.remove(f.path)
                nb += 1
            for fw in f.files_web:
                session.delete(fw)
            session.delete(f)
            session.commit()
        print "Removed {0} files older than {1}".format(nb, humanize_time_str(max_age, 'seconds'))

clean_db()
