from flask import jsonify, g, request
from flask_restful import Resource
from datetime import datetime
import json
from helpers.vk import VK
from helpers.time import getCurrentTimestamp
from helpers.book import getUsersPublicBooks
from threading import Thread

from helpers.jsonify_models import dict_userself, dict_user
from helpers.datetime_checker import get_date_for_init

from db.models import User, Moodes, Questions, Settings

vk_api = VK()

timeout_reload = 7 * 24 * 60 * 60


def vk_profile_reload(user):
    user_profile = vk_api.get_user(user.vk_id)
    timenow = int(datetime.now().timestamp())

    user.first_name = user_profile['first_name']
    user.last_name = user_profile['last_name']
    user.photo = user_profile['photo_200']
    user.timestamp_vk_reload = timenow
    user.save()


def getUsersMoodOfDay(user, day, month, year):
    res = Moodes.select().where(
        (Moodes.user == user) & (Moodes.day == day) & (Moodes.month == month) & (Moodes.year == year))
    if len(res) == 0:
        return -1

    return res[0].mood


def getCurrentDay():
    return dict(
        day=datetime.now().day,
        month=datetime.now().month,
        year=datetime.now().year
    )


class UserInit(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        user = User.select().where(User.vk_id == userid)
        timenow = getCurrentTimestamp()
        open_first = False
        if len(user) == 0:
            open_first = True
            time_offset = 0
            if 'offset' in r.keys() and type(r['offset']) == int and (-24 <= r['offset'] <= 24):
                time_offset = r['offset']

            user_profile = vk_api.get_user(userid)
            user = User(
                vk_id=userid,
                first_name=user_profile['first_name'],
                last_name=user_profile['last_name'],
                photo=user_profile['photo_200'],
                timestamp_reg=timenow,
                timestamp_vk_reload=timenow,
                time_offset=time_offset
            )
            user.save()

            settings = Settings(user=user)
            settings.save()
        else:
            user = user[0]
            if (timenow - user.timestamp_vk_reload) >= timeout_reload:
                reload_thread = Thread(target=vk_profile_reload, args=(user,))
                reload_thread.start()

            if 'offset' in r.keys() and type(r['offset']) == int and (-24 <= r['offset'] <= 24):
                user.time_offset = r['offset']
                user.save()

        date_init = get_date_for_init(r, user)

        user_response = dict_userself(user, date_init['day'], date_init['month'], date_init['year'])
        user_response['open_first'] = open_first

        return dict(
            code=200,
            error=False,
            user=user_response
        ), 200


class SetTimeOffset(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if ('offset' not in r.keys()) or type(r['offset']) != int or r['offset'] < -24 or r['offset'] > 24:
            r['offset'] = 0

        user = User.get(User.vk_id == userid)
        user.time_offset = r['offset']
        user.save()

        return dict(
            error=False,
            code=200,
            time_offset=r['offset'],
            message='Временной пояс успешно изменён'
        ), 200

class GetProfile(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'userid' not in r.keys() or type(r['userid']) != int:
            return dict(
                error=True,
                code=400,
                message='Неверный ID пользователя'
            ), 400

        users = User.select().where(User.vk_id == r['userid'])
        if len(users) == 0:
            return dict(
                error=True,
                code=404,
                message='Пользователь не найден'
            ), 404
        user = users[0]


        return dict(
            error=False,
            code=200,
            user=dict(
                user=dict_user(user),
                mood_public=user.settings[0].mood_public,
                public_books=getUsersPublicBooks(user)
            )
        )


class AddQuestion(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if userid != 296223969:
            return dict(error=True, create=False), 400

        q = Questions(
            question=r['question'],
            description=r['description'],
            type=r['type'],
            day_index=r['day_index']
        )
        q.save()

        return dict(error=False, create=True)