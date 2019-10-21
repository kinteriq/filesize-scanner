from datetime import datetime
from dateutil.relativedelta import relativedelta
import stat
import time


def useless_file(path):     # TODO: all platforms
    """
    Check when the file was last opened;
        returns True if more time had passed
        than specified in FILES_NOT_USED.
    """
    today = datetime.today()
    delta = today - relativedelta(**FILES_NOT_USED)
    last_modified = os.stat(path)[stat.ST_ATIME]
    if last_modified < time.mktime(delta.timetuple()):
        return True
    return False
