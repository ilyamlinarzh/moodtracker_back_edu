from flask import g, request, jsonify
from flask_restful import Resource
import json
from datetime import datetime
from uuid import uuid4

from db.models import User, Diary, Post, Member, Attachment, Questions
from helpers.json_checker import isJson
from helpers.datetime_checker import canPostInDate
from helpers.jsonify_models import dict_post, dict_attachment, dict_post_with_attachments
from helpers.time import getCurrentTimestamp, get_utc_timestamp
from helpers.permission_checker import canCreatePost, canAddAttachment, canVisitBook, isAdmin
from helpers.mood import setMood
from helpers.extraQ import markExtraQ
from helpers.text_workers import textInputLength

mood_maxscore = 13
extrajson_maxlen = 1500
text_maxlen = 2500

page_size = 12

attachments_types = ['photobase']
order_by_types = ['desc', 'asc']


def getCorrectAttachments(att):
    if len(att) > 10:
        return []

    correct_att = []
    for at in att:
        if type(at) != dict:
            continue
        if 'type' not in at.keys() or at['type'] not in attachments_types:
            continue
        if 'content' not in at.keys() or not isJson(at['content']):
            continue

        content_json = json.loads(at['content'])
        if 'photo' in content_json.keys():
            if type(content_json['photo']) != str:
                continue
            if not content_json['photo'].startswith('https://'):
                continue

        attachment_id = str(uuid4())
        correct_att.append(dict(
            attachment_id=attachment_id,
            type=at['type'],
            content=at['content']
        ))

    return correct_att


class AddAttachment(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)
        if 'post_id' not in r.keys() or type(r['post_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Некорреткный идентификатор записи'
            ), 400

        if 'attachments' not in r.keys() or type(r['attachments']) != list:
            return dict(
                error=True,
                code=400,
                message='Некорреткный список вложений'
            ), 400

        posts = Post.select().where(
            Post.post_id == r['post_id']
        )
        if len(posts) == 0:
            return dict(
                error=True,
                code=404,
                message='Этой записи не существует'
            ), 404
        post = posts[0]

        attachments = getCorrectAttachments(r['attachments'])

        if not canAddAttachment(post, len(attachments)):
            return dict(
                error=True,
                code=400,
                message='Нельзя добавлять более 10 вложений'
            ), 400

        user = User.get(User.vk_id == userid)

        if post.author.vk_id != userid:
            return dict(
                error=True,
                code=403,
                message='Нет прав'
            ), 403

        Attachment.insert_many(
            [dict(**a, author=user, post=post) for a in attachments]
        ).execute()

        return dict(
            error=False,
            code=200,
            message='Вложение добавлено',
            attachments=attachments
        )


class NewPost(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Неверный идентификатор дневника'
            ), 400

        mood = -1
        if 'mood' in r.keys() and type(r['mood']) == int and (0 <= r['mood'] <= mood_maxscore):
            mood = r['mood']

        extra_content = {}
        if 'extra_content' in r.keys() and len(r['extra_content']) <= extrajson_maxlen and isJson(r['extra_content']):
            extra_content = json.loads(r['extra_content'])

        if 'text' not in r.keys() or type(r['text']) != str or textInputLength(r['text']) > text_maxlen:
            return dict(
                error=True,
                code=400,
                message='Некорректный текст записки'
            ), 400

        if 'day' not in r.keys() or type(r['day']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректная дата'
            ), 400

        if 'month' not in r.keys() or type(r['month']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректная дата'
            ), 400

        if 'year' not in r.keys() or type(r['year']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректная дата'
            ), 400

        user = User.get(User.vk_id == userid)

        if not canPostInDate(r['day'], r['month'], r['year'], user.time_offset):
            return dict(
                error=True,
                code=400,
                message='Создать записку на этот день уже нельзя'
            ), 400

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Дневник не существует'
            ), 404
        book = books[0]
        if not canCreatePost(user, book):
            return dict(
                error=True,
                code=400,
                message='Вы не состоите в этом дневнике'
            ), 400

        post_id = str(uuid4())
        post = Post(
            post_id=post_id,
            book=book,
            author=user,
            text=r['text'],
            extra_content=json.dumps(extra_content),
            timestamp_create=getCurrentTimestamp(),
            day=r['day'],
            month=r['month'],
            year=r['year'],
            timestamp_thisday=get_utc_timestamp(r['day'], r['month'], r['year'])
        )
        post.save()

        if mood >= 0:
            setMood(user, r['day'], r['month'], r['year'], mood)

        if 'extraQ' in extra_content.keys():
            if 'question' in extra_content['extraQ'].keys():
                markExtraQ(user, extra_content['extraQ']['question'], r['day'], r['month'], r['year'])
                Questions.update(
                    uses=Questions.uses+1
                ).where(Questions.question == extra_content['extraQ']['question']).execute()

        return dict(
            error=False,
            code=200,
            message='Запись была сохранена',
            create=True,
            post=dict_post(post)
        )

class EditTextPost(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'post_id' not in r.keys() or type(r['post_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Некорректный идентификатор записи'
            ), 400

        if 'text' not in r.keys() or type(r['text']) != str or len(r['text']) > text_maxlen:
            return dict(
                error=True,
                code=400,
                message='Некорректный текст записки'
            ), 400

        posts = Post.select().where(Post.post_id == r['post_id'])
        if len(posts) == 0:
            return dict(
                error=True,
                code=404,
                message='Запись не найдена'
            ), 404
        post = posts[0]

        if post.author.vk_id != userid:
            return dict(
                error=True,
                code=403,
                message='Нет прав'
            ), 403

        post.text = r['text']
        post.save()


        return dict(
            error=False,
            edit=True,
            text=r['text'],
            message='Записка изменена'
        )



class GetPost(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'post_id' not in r.keys() or type(r['post_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Некорректный идентификатор записи'
            ), 400

        posts = Post.select().where(Post.post_id == r['post_id'])
        if len(posts) == 0:
            return dict(
                error=True,
                code=404,
                message='Запись не найдена'
            ), 404
        post = posts[0]

        user = User.get(User.vk_id == userid)
        if not canVisitBook(user, post.book):
            return dict(
                error=True,
                code=403,
                message='У вас нет доступа к этой записи'
            ), 403

        return dict(
            error=False,
            code=200,
            post=dict_post_with_attachments(post)
        )


class RemovePost(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'post_id' not in r.keys() or type(r['post_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Некорректный идентификатор записи'
            ), 400

        posts = Post.select().where(Post.post_id == r['post_id'])
        if len(posts) == 0:
            return dict(
                error=True,
                code=404,
                message='Эта запись не существует'
            ), 404
        post = posts[0]
        user = User.get(User.vk_id == userid)
        if not isAdmin(user, post.book) and post.book.author.vk_id != userid:
            return dict(
                error=True,
                code=403,
                message='Нет прав'
            ), 403

        Attachment.delete().where(
            Attachment.post == post
        ).execute()
        post.delete_instance()
        return dict(
            error=False,
            code=200,
            postid=r['post_id'],
            message='Запись была удалена'
        )


class GetBooksPosts(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'book_id' not in r.keys() or type(r['book_id']) != str:
            return dict(
                error=True,
                code=400,
                message='Некорректный идентификатор дневника'
            ), 400

        page = 0
        if 'page' in r.keys() and type(r['page']) == int and (0 <= r['page'] <= 1500):
            page = r['page']

        user = User.get(User.vk_id == userid)

        books = Diary.select().where(Diary.book_id == r['book_id'])
        if len(books) == 0:
            return dict(
                error=True,
                code=404,
                message='Этого дневника не существует'
            )
        book = books[0]

        if not canVisitBook(user, book):
            return dict(
                error=True,
                code=403,
                message='Нет доступа'
            ), 403

        posts = Post.select().where(Post.book == book).offset(page * page_size).limit(page_size)
        posts = [dict_post(p) for p in posts]

        return dict(
            error=False,
            code=200,
            page=page,
            posts=posts
        ), 200


class GetPosts(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        page = 0
        if 'page' in r.keys() and type(r['page']) == int and (0 <= r['page'] <= 1500):
            page = r['page']

        user = User.get(User.vk_id == userid)
        books = [m.book.book_id for m in user.members]

        posts = Post.select().where(Post.book.book_id.in_(books))


class GetPostsByBookIds(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'books' not in r.keys() or type(r['books']) != list or len(r['books']) > 15 or len(r['books']) == 0:
            return dict(
                error=True,
                code=400,
                message='Некорректные идентификаторы дневников'
            ), 400

        page = 0
        if 'page' in r.keys() and type(r['page']) == int and (0 <= r['page'] <= 1500):
            page = r['page']

        order_by = 'desc'
        if 'order_by' in r.keys() and r['order_by'] in order_by_types:
            order_by = r['order_by']

        books_ids = set(r['books'])

        user = User.get(User.vk_id == userid)

        user_books_join = [b.book.book_id for b in user.members]
        user_books = [b.book_id for b in user.books] + user_books_join
        user_books_join_ids = set(user_books)

        books = list(books_ids & user_books_join_ids)

        if len(books) == 0:
            return dict(
                error=True,
                code=400,
                message='Вы не состоите ни в одном из переданных дневников'
            )

        books_models = Diary.select().where(Diary.book_id.in_(books))
        posts = Post.select().where(Post.book.in_(books_models))
        if order_by == 'desc':
            posts = posts.order_by(Post.timestamp_thisday.desc(), Post.timestamp_create.desc())
        elif order_by == 'asc':
            posts = posts.order_by(Post.timestamp_thisday.asc(), Post.timestamp_create.asc())
        posts = posts.offset(page * page_size).limit(page_size)
        posts = [dict_post(p) for p in posts]

        return dict(
            error=False,
            code=200,
            page=page,
            order_by=order_by,
            posts=posts
        ), 200

class GetPostsByBookIdsInDay(Resource):
    def post(self):
        userid = g.get('userid')
        r = json.loads(request.data)

        if 'books' not in r.keys() or type(r['books']) != list or len(r['books']) > 15 or len(r['books']) == 0:
            return dict(
                error=True,
                code=400,
                message='Некорректные идентификаторы дневников'
            ), 400

        if 'day' not in r.keys() or type(r['day']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректная дата'
            ), 400

        if 'month' not in r.keys() or type(r['month']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректная дата'
            ), 400

        if 'year' not in r.keys() or type(r['year']) != int:
            return dict(
                error=True,
                code=400,
                message='Некорректная дата'
            ), 400

        books_ids = set(r['books'])

        user = User.get(User.vk_id == userid)

        user_books_join = [b.book.book_id for b in user.members]
        user_books = [b.book_id for b in user.books] + user_books_join
        user_books_join_ids = set(user_books)

        books = list(books_ids & user_books_join_ids)

        if len(books) == 0:
            return dict(
                error=True,
                code=400,
                message='Вы не состоите ни в одном из переданных дневников'
            )

        books_models = Diary.select().where(Diary.book_id.in_(books))
        posts = Post.select().where(
            (Post.book.in_(books_models)) &
            (Post.day == r['day']) &
            (Post.month == r['month']) &
            (Post.year == r['year'])
        )
        posts = posts.order_by(Post.timestamp_thisday.desc(), Post.timestamp_create.desc())
        posts = posts.limit(25)
        posts = [dict_post(p) for p in posts]

        return dict(
            error=False,
            code=200,
            posts=posts
        ), 200