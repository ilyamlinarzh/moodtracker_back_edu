from datetime import datetime, timezone, timedelta


def get_utc_timestamp(day, month, year):
    dt = datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc)
    offset = timedelta(hours=dt.astimezone().utcoffset().total_seconds() / 3600)
    utc_dt = dt - offset
    return int(utc_dt.timestamp())

def get_utc_timestamp_endday(day, month, year):
    dt = datetime(year, month, day, 23, 59, 59, tzinfo=timezone.utc)
    offset = timedelta(hours=dt.astimezone().utcoffset().total_seconds() / 3600)
    utc_dt = dt - offset
    return int(utc_dt.timestamp())

def get_utc_timestamp_endday_by_timestamp(timestamp):
    utc_date = datetime.utcfromtimestamp(timestamp)
    dt = datetime(utc_date.year, utc_date.month, utc_date.day, 23, 59, 59, tzinfo=timezone.utc)
    offset = timedelta(hours=dt.astimezone().utcoffset().total_seconds() / 3600)
    utc_dt = dt - offset
    return int(utc_dt.timestamp()) + 1

def get_utc_timestamp_startday_by_timestamp(timestamp):
    utc_date = datetime.utcfromtimestamp(timestamp)
    dt = datetime(utc_date.year, utc_date.month, utc_date.day, 0, 0, 0, tzinfo=timezone.utc)
    offset = timedelta(hours=dt.astimezone().utcoffset().total_seconds() / 3600)
    utc_dt = dt - offset
    return int(utc_dt.timestamp())

def getCurrentTimestamp():
    dt = datetime.now()
    offset = timedelta(hours=dt.astimezone().utcoffset().total_seconds() / 3600)
    utc_dt = dt - offset
    return int(utc_dt.timestamp())

def get_date_with_offset(offset, starttime=getCurrentTimestamp()):
    timenow_offset = starttime + (offset*60*60)
    date = datetime.fromtimestamp(timenow_offset)
    return dict(
        day=date.day,
        month=date.month,
        year=date.year
    )