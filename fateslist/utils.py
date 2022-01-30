import datetime
import traceback

def extract_time(td: datetime.timedelta) -> tuple:
    """
    Extracts time from a timedelta object.
    
    usage: (_d, _h, _m, _s, _mils, _mics) = tdTuple(td)
    """
    def _t(t, n):
        if t < n:
            return (t, 0)
        v = t // n
        return (t - (v * n), v)

    (s, h) = _t(td.seconds, 3600)
    (s, m) = _t(s, 60)
    return (td.days, h, m, s)

def etrace(ex):
    """
    Get the traceback of an exception

    Used internally by fateslist.py and our own tooling
    """
    try:
        return "".join(traceback.format_exception(ex)) # COMPAT: Python 3.10 only
    except:
        return str(ex)
