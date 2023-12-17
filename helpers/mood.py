from db.models import Moodes
from datetime import datetime
from helpers.time import get_utc_timestamp, getCurrentTimestamp

def getMood(user, day, month, year):
    res = Moodes.select().where((Moodes.user == user) &
                                (Moodes.day == day) &
                                (Moodes.month == month) &
                                (Moodes.year == year))

    if len(res) == 0:
        return -1

    return res[0].mood

def setMood(user, day, month, year, mood):
    res = Moodes.select().where((Moodes.user == user) &
                                (Moodes.day == day) &
                                (Moodes.month == month) &
                                (Moodes.year == year))

    if len(res) == 0:
        mood_r = Moodes(
            user=user,
            day=day,
            month=month,
            year=year,
            timestamp_thisday=get_utc_timestamp(day, month, year),
            timestamp_create=getCurrentTimestamp(),
            mood=mood
        )
        mood_r.save()
    else:
        Moodes.update(mood=mood).where(
                                (Moodes.user == user) &
                                (Moodes.day == day) &
                                (Moodes.month == month) &
                                (Moodes.year == year)).execute()

