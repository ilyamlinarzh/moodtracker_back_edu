from flask_restful import Resource
from flask import request, g
import json
from db.models import Member, Diary, User
from helpers.book import getUsersBook_ids
from helpers.jsonify_models import dict_user

class LeaveBook(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'bookid' not in r.keys() or type(r['bookid']) != str:
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
        if book.author.vk_id == userid:
            return dict(
                error=True,
                code=400,
                leave=False,
                message='Вы не можете выйти из дневника, так как вы являетесь администратором'
            )

        user = User.get(User.vk_id == userid)

        members = Member.select().where(
            (Member.member == user) &
            (Member.book == book)
        )
        if len(members) == 0:
            return dict(
                error=True,
                code=403,
                message='Вы не являетесь участником этого дневника'
            )

        member = members[0]
        member.delete_instance()

        return dict(
            error=False,
            code=200,
            leave=True,
            message=f'Вы покинули дневник "{member.book.name}"'
        )

class GetMembers(Resource):
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

        books_join = getUsersBook_ids(user)

        if book.book_id not in books_join:
            return dict(
                error=True,
                code=403,
                message='Вы не участник этого дневника'
            ), 403

        members = []
        members_ids = []
        for mu in book.members:
            if mu.member.vk_id not in members_ids:
                members.append(dict_user(mu.member))
                members_ids.append(mu.member.vk_id)
        # members = [dict_user(u.member) for u in book.members]

        return dict(
            error=False,
            code=200,
            members=members
        )

class KickMember(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный ID дневника'
            ), 400

        if 'userid' not in r.keys() or type(r['userid']) != int:
            return dict(
                error=True,
                code=400,
                message='Неверный ID пользователя'
            ), 400

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Дневник не найден'
            ), 404

        book = books[0]

        if book.author.vk_id != userid:
            return dict(
                error=True,
                code=403,
                message='Вы не администратор этого дневника'
            )

        users = User.select().where(User.vk_id == r['userid'])
        if len(users) == 0:
            return dict(
                error=True,
                code=404,
                messages='Пользователь не найден'
            )
        user = users[0]

        Member.delete().where(
            (Member.book == book) &
            (Member.member == user)
        ).execute()

        return dict(
            error=False,
            code=200,
            userid=r['userid'],
            kick=True
        )