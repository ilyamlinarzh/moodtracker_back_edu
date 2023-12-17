from flask_restful import Resource
from flask import request, g
from db.models import User, Diary, Member, Invite, Post
import json
from uuid import uuid4
from datetime import datetime

from helpers.jsonify_models import dict_book, dict_member_book
from helpers.permission_checker import canJoinInBook, canVisitBook
from helpers.time import getCurrentTimestamp
from helpers.book import getUsersBook, removeBook

max_users_books = 5
mode_variables = ['person', 'public']
description_max_length = 300
name_max_length = 30


class NewDiary(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        mode = 'person'
        if 'mode' in r.keys() and r['mode'] in mode_variables:
            mode = r['mode']

        description = ''
        if 'description' in r.keys() and type(r['description']) == str and len(
                r['description']) <= description_max_length:
            description = r['description']

        name = ''
        if 'name' in r.keys() and type(r['name']) == str and len(r['name']) <= name_max_length:
            name = r['name']

        user = User.get(User.vk_id == userid)
        if not canJoinInBook(user):
            return dict(
                error=False,
                code=200,
                create=False,
                message='Вы создали слишком много дневников'
            )

        book_id = str(uuid4())
        timeNow = getCurrentTimestamp()
        book = Diary(
            book_id=book_id,
            author=user,
            mode=mode,
            name=name,
            description=description,
            timestamp_create=timeNow
        )
        book.save()

        return dict(
            error=False,
            code=200,
            create=True,
            book=dict_book(book)
        )


class EditDiary(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if ('mode' not in r.keys()) or (r['mode'] not in mode_variables):
            return dict(
                error=True,
                code=400,
                message='Неверное значение mode'
            ), 400

        if ('description' not in r.keys()) or (type(r['description']) != str) or (len(
                r['description']) > description_max_length):
            return dict(
                error=True,
                code=400,
                message='Неверное значение описания'
            ), 400

        if ('name' not in r.keys()) or (type(r['name']) != str) or (len(r['name']) > name_max_length):
            return dict(
                error=True,
                code=400,
                message='Неверное значение названия'
            ), 400

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверное идентификатора дневника'
            ), 400

        user = User.get(User.vk_id == userid)
        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Этого дневника не существует'
            ), 404
        book = books[0]

        if book.author.vk_id != userid:
            return dict(
                error=True,
                code=403,
                message='Нет прав'
            ), 403

        Diary.update(
            name=r['name'],
            description=r['description'],
            mode=r['mode']
        ).where(Diary.book_id == r['book_id']).execute()

        if r['mode'] == 'public' and book.mode != r['mode']:
            Invite.delete().where(
                Invite.book==book
            ).execute()

        return dict(
            error=False,
            code=200,
            edits=dict(
                mode=r['mode'],
                name=r['name'],
                description=r['description']
            ),
            message='Дневник был отредактирован'
        )

class RemoveDiary(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный идентификатор дневника'
            ), 400

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Этого дневника не существует'
            ), 404

        book = books[0]
        user = User.get(User.vk_id == userid)

        if book.author.vk_id != user.vk_id:
            return dict(
                error=False,
                code=403,
                message='Вы не администратор этого дневника'
            ), 403

        removeBook(book)
        return dict(
            error=False,
            code=200,
            book_id=r['book_id'],
            message=f'Дневник {book.name} был удалён'
        )

class GetBooks(Resource):
    def post(self):
        userid = g.get('userid')

        user = User.get(User.vk_id == userid)
        books = getUsersBook(user)

        return dict(
            error=False,
            code=200,
            userid=userid,
            books=books
        ), 200


class GetBooksByJoin(Resource):
    def post(self):
        userid = g.get('userid')

        user = User.get(User.vk_id == userid)
        books = [dict_member_book(mb) for mb in user.members]

        return dict(
            error=False,
            code=200,
            userid=userid,
            books=books
        ), 200


class GetDiary(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный идентификатор дневника'
            ), 400

        user = User.get(User.vk_id == userid)

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message="Этого дневника не существует"
            ), 404
        book:Diary = books[0]

        if not canVisitBook(user, book):
            return dict(
                error=True,
                code=403,
                message='Вы не имеете доступ к этому дневнику'
            ), 403

        return dict(
            error=False,
            code=200,
            book=dict_book(book)
        )
