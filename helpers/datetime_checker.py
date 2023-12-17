from datetime import datetime
from helpers.time import get_date_with_offset, get_date_with_offset, getCurrentTimestamp, get_utc_timestamp

back_timeaccess = 365*24*60*60*0.5
forward_timeaccess = 3*24*60*60
def is_valid_date(y, m, d):
    try:
        timestamp = datetime.strptime(f'{y}-{m}-{d}', '%Y-%m-%d').timestamp()
        return (True, timestamp)
    except ValueError:
        return (False,)

def can_create_write(y,m,d):
    r = is_valid_date(y,m,d)
    if not r[0]: return False

    timeNow = datetime.now().timestamp()
    d = timeNow-r[1]
    if d > 0:
        if d > back_timeaccess: return False
    else:
        if abs(d) > forward_timeaccess: return False

    return True

def get_date_for_init(r, user):
    if 'day' not in r.keys() or 'month' not in r.keys() or 'year' not in r.keys():
        date = get_date_with_offset(user.time_offset)
    else:
        d = is_valid_date(r['year'], r['month'], r['day'])
        print(d)
        if not d[0]:
            date = get_date_with_offset(user.time_offset)
        else:
            date = dict(
                day=int(r['day']),
                month=int(r['month']),
                year=int(r['year'])
            )

    return date

def canPostInDate(d, m, y, time_offset):
    current_ts = getCurrentTimestamp()
    dt = get_date_with_offset(offset=time_offset, starttime=current_ts)
    dt_9h_ago = get_date_with_offset(offset=time_offset, starttime=current_ts-(9*60*60))
    if dt['day'] == d and dt['month'] == m and dt['year'] == y:
        return True

    if dt_9h_ago['day'] == d and dt_9h_ago['month'] == m and dt_9h_ago['year'] == y:
        return True

    return False

def canSetMoodInDate(d, m, y, time_offset):
    current_ts = getCurrentTimestamp()
    thisday_ts = get_utc_timestamp(d, m, y)

    return current_ts >= thisday_ts