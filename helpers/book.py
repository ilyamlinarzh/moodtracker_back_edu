from db.models import User, Member, Diary, Post, Invite
from helpers.jsonify_models import dict_book

def getUsersBook(user):
    books_m = [m.book for m in user.members]

    return [dict_book(b) for b in user.books] + [dict_book(b) for b in books_m]

def getUsersBook_ids(user):
    books_m = [m.book for m in user.members]

    return [b.book_id for b in user.books] + [b.book_id for b in books_m]

def getUsersPublicBooks(user):
    books_req = Diary.select().where(
        (Diary.author == user) &
        (Diary.mode == 'public')
    )

    return [dict_book(b) for b in books_req]

def removeBook(book: Diary):
    book.delete_instance()
    Post.delete().where(Post.book == book).execute()
    Invite.delete().where(Invite.book == book).execute()
    Member.delete().where(Member.book == book).execute()