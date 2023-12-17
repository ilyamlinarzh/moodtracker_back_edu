from flask import g, request
from flask_restful import Resource
from db.models import Moodes, User, Settings
from helpers.datetime_checker import is_valid_date
from helpers.jsonify_models import dict_moodes
from helpers.datetime_checker import canPostInDate, canSetMoodInDate
import json
from helpers.time import getCurrentTimestamp

class GetMoodes(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'month' not in r.keys() or type(r['month']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректное значение месяца'
            ), 400

        if 'year' not in r.keys() or type(r['year']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректное значение года'
            ), 400

        date = is_valid_date(r['year'], r['month'], 1)
        if not date[0]:
            return dict(
                error=True,
                code=400,
                message='Некорректные значения периода'
            ), 400

        if 'userid' in r.keys() and type(r['userid']) == int and (userid!=r['userid']):
            user_fetch_req = User.select().where(
                User.vk_id == r['userid']
            )
            if len(user_fetch_req) == 0:
                return dict(
                    error=True,
                    code=404,
                    messages='Пользователь не найден'
                ), 404
            user_fetch = user_fetch_req[0]
            if not (user_fetch.settings[0].mood_public or userid==r['userid']):
                return dict(
                    error=True,
                    code=403,
                    messages='Нет доступа'
                ), 403
        else:
            user_fetch = User.get(User.vk_id==userid)

        moodes = Moodes.select().where(
            (Moodes.user==user_fetch) &
            (Moodes.timestamp_thisday.between(date[1]-(7*24*60*60), date[1]+(30*24*60*60)+(7*24*60*60)))
        )
        moodes = [dict_moodes(m) for m in moodes]

        return dict(
            error=False,
            code=200,
            moodes=moodes
        )

class SetMood(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'day' not in r.keys() or type(r['day']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректное значение дня'
            ), 400

        if 'month' not in r.keys() or type(r['month']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректное значение месяца'
            ), 400

        if 'year' not in r.keys() or type(r['year']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректное значение года'
            ), 400

        if 'mood' not in r.keys() or type(r['mood']) != int or (not (1<=r['mood']<=7)):
            return dict(
                error=True,
                code=400,
                message='Некорректное значение настроения'
            ), 400

        date = is_valid_date(r['year'], r['month'], r['day'])
        if not date[0]:
            return dict(
                error=True,
                code=400,
                message='Некорректные значения дня'
            ), 400

        user = User.get(User.vk_id == userid)

        if not canSetMoodInDate(r['day'], r['month'], r['year'], user.time_offset):
            return dict(
                error=True,
                code=400,
                message='Вы не можете установить настроение на этот день'
            )

        user = User.get(User.vk_id==userid)
        moodes_req = Moodes.select().where(
            (Moodes.day==r['day']) &
            (Moodes.month==r['month']) &
            (Moodes.year==r['year']) &
            (Moodes.user==user)
        )

        if len(moodes_req) > 0:
            mood = moodes_req[0]
            mood.mood = r['mood']
        else:
            timeNow = getCurrentTimestamp()
            mood = Moodes(
                user=user,
                day=r['day'],
                month=r['month'],
                year=r['year'],
                timestamp_thisday=date[1],
                timestamp_create=timeNow,
                mood=r['mood']
            )
        mood.save()

        return dict(
            error=False,
            code=200,
            mood=r['mood'],
            date=dict(
                day=r['day'],
                month=r['month'],
                year=r['year']
            )
        )