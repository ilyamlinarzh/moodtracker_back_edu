from flask_restful import Resource
from flask import request, g
from db.models import User, Settings
import json

class SetExtras(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        extraQ = False
        if 'extraQ' in r.keys() and type(r['extraQ']) == bool:
            extraQ = r['extraQ']

        unusualExtraQ = False
        if 'unusualExtraQ' in r.keys() and type(r['unusualExtraQ']) == bool:
            unusualExtraQ = r['unusualExtraQ']

        user = User.get(User.vk_id == userid)
        settings = Settings.get(Settings.user == user)

        settings.extraQ = extraQ
        settings.unusualExtraQ = unusualExtraQ
        settings.save()

        return dict(
            error=False,
            code=200,
            extraQ=extraQ,
            unusualExtraQ=unusualExtraQ,
            message='Настройки были изменены'
        )

class SetPublicParameters(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        mood_public = False
        if 'mood_public' in r.keys() and type(r['mood_public']) == bool:
            mood_public = r['mood_public']

        profile_button = False
        if 'profile_button' in r.keys() and type(r['profile_button']) == bool:
            profile_button = r['profile_button']

        user = User.get(User.vk_id == userid)
        settings = Settings.get(Settings.user == user)

        settings.mood_public = mood_public
        settings.profile_button = profile_button
        settings.save()

        return dict(
            error=False,
            code=200,
            mood_public=mood_public,
            profile_button=profile_button,
            message='Настройки были изменены'
        )

class SetNotifications(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        app_notify = False
        if 'app_notify' in r.keys() and type(r['app_notify']) == bool:
            app_notify = r['app_notify']

        messages_notify = False
        if 'messages_notify' in r.keys() and type(r['messages_notify']) == bool:
            messages_notify = r['messages_notify']

        user = User.get(User.vk_id == userid)
        settings = Settings.get(Settings.user == user)

        settings.app_notify = app_notify
        settings.messages_notify = messages_notify
        settings.save()

        return dict(
            error=False,
            code=200,
            app_notify=app_notify,
            messages_notify=messages_notify,
            message='Настройки были изменены'
        )