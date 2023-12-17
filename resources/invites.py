from flask_restful import Resource
from flask import request, g
from helpers.permission_checker import isAdmin, mayCreateInvite
from helpers.jsonify_models import dict_invite
from helpers.book import getUsersBook_ids
from helpers.time import getCurrentTimestamp
from db.models import Diary, User, Invite, Member
from uuid import uuid4
import json

class CreateInvite(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный ID дневника'
            ), 400

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Дневник не найден'
            ), 404

        book = books[0]
        if book.mode == 'public':
            return dict(
                error=True,
                code=200,
                message='Нельзя создать хэш-приглашение для публичного дневника'
            )
        recreate = len(book.invites) > 0
        if recreate:
            Invite.delete().where(Invite.book == book).execute()

        user = User.get(User.vk_id == userid)
        if not isAdmin(user, book):
            return dict(
                error=True,
                code=403,
                message='Вы не являетесь администратором этого дневника'
            )

        invitehash = str(uuid4())
        invite = Invite(
            author=user,
            book=book,
            hash=invitehash
        )
        invite.save()

        return dict(
            error=False,
            code=200,
            invite=dict_invite(invite),
            recreate=recreate
        )

class DeleteInvite(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'hash' not in r.keys() or type(r['hash']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный hash приглашения'
            ), 400

        invites = Invite.select().where(Invite.hash == r['hash'])
        if len(invites) == 0:
            return dict(
                error=True,
                code=404,
                message='Этого приглашения не существует'
            ), 404

        invite = invites[0]
        user = User.get(User.vk_id == userid)

        if not isAdmin(user, invite.book):
            return dict(
                error=True,
                code=403,
                message='Вы не администратор дневника, к которому создано это приглашение'
            ), 404

        invite.delete_instance()

        return dict(
            error=False,
            code=200,
            delete=True,
            message='Приглашение удалено'
        )

class GetInvite(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный ID дневника'
            ), 400

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Дневник не найден'
            ), 404

        book = books[0]
        user = User.get(User.vk_id == userid)

        if not isAdmin(user, book):
            return dict(
                error=True,
                code=403,
                message='Вы не администратор дневника'
            ), 404

        invites = Invite.select().where(Invite.book == book)
        if len(invites) == 0:
            return dict(
                error=False,
                code=200,
                invite=False
            )
        invite = invites[0]

        return dict(
            error=False,
            code=200,
            invite=dict_invite(invite)
        )

class JoinByInvite(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'hash' not in r.keys() or type(r['hash']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный hash приглашения'
            ), 400

        invites = Invite.select().where(Invite.hash == r['hash'])
        if len(invites) == 0:
            return dict(
                error=True,
                code=404,
                message='Этого приглашения не существует',
                join=False
            ), 404

        invite = invites[0]
        user = User.get(User.vk_id == userid)
        bookid = invite.book.book_id
        users_join = getUsersBook_ids(user)

        if bookid in users_join:
            return dict(
                error=True,
                code=400,
                message='Вы уже являетесь участником этого дневника',
                join=True
            )
        timeNow = getCurrentTimestamp()

        member = Member(
            book=invite.book,
            member=user,
            mode='write',
            timestamp_join=timeNow
        )
        member.save()

        return dict(
            error=False,
            code=200,
            message=f'Вы присоединились к дневнику "{invite.book.name}"',
            join=True
        )