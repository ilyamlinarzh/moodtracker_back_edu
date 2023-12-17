from db.models import Member, User

max_attachments = 10
max_users_books = 5

def canCreatePost(user, book):
    if book.author.vk_id == user.vk_id:
        return True

    res = Member.select().where(
        (Member.book == book) &
        (Member.member == user)
    )

    if len(res) == 0:
        return False

    if res[0].mode == 'write':
        return True

    return False


def canVisitBook(user, book):
    if book.mode == 'public':
        return True

    if book.author.vk_id == user.vk_id:
        return True

    res = Member.select().where(
        (Member.book == book) &
        (Member.member == user)
    )

    if len(res) == 0:
        return False

    if res[0].mode in ['write', 'read']:
        return True

    return False

def isAdmin(user, book):
    if book.author.vk_id == user.vk_id:
        return True

    return False

def canAddAttachment(post, count=1):
    if (len(post.attachments)+count) > max_attachments:
        return False

    return True

def canJoinInBook(user):
    result_count = len(user.books)+len(user.members)
    return result_count < max_users_books

def mayCreateInvite(book):
    return book.invites < 3