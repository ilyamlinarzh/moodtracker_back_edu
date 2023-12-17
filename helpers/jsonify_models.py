import json
from helpers.mood import getMood
from helpers.extraQ import needXQ, getQuestion
from helpers.funcs import stringNum


def dict_user(model):
    return dict(
        userid=model.vk_id,
        first_name=model.first_name,
        last_name=model.last_name,
        photo=model.photo
    )


def dict_book(model):
    return dict(
        book_id=model.book_id,
        name=model.name,
        description=model.description,
        author=dict_user(model.author),
        mode=model.mode
    )


def dict_book_small(model):
    return dict(
        book_id=model.book_id,
        name=model.name,
        author_id=model.author.vk_id
    )


def dict_post(model):
    return dict(
        post_id=model.post_id,
        book=dict_book_small(model.book),
        author=dict_user(model.author),
        text=model.text,
        date=dict(
            day=model.day,
            month=model.month,
            year=model.year,
            timestamp=model.timestamp_thisday
        ),
        extra_content=json.loads(model.extra_content),
        timestamp_create=model.timestamp_create,
        attachments_count=len(model.attachments)
    )


def dict_member_book(model):
    return {**dict_book(model.book), 'join_mode': model.mode}


def dict_attachment(model):
    return dict(
        attachment_id=model.attachment_id,
        type=model.type,
        content=json.loads(model.content)
    )

def dict_post_with_attachments(model):
    return dict(
        post_id=model.post_id,
        book=dict_book_small(model.book),
        author=dict_user(model.author),
        text=model.text,
        date=dict(
            day=model.day,
            month=model.month,
            year=model.year,
            timestamp=model.timestamp_thisday
        ),
        extra_content=json.loads(model.extra_content),
        timestamp_create=model.timestamp_create,
        attachments_count=len(model.attachments),
        attachments=[dict_attachment(a) for a in model.attachments]
    )

def dict_userself(user, d, m, y):
    users_settings = user.settings[0]
    extraQ = needXQ(user, d, m, y)
    res = dict(
        user=dict(
            userid=user.vk_id,
            first_name=user.first_name,
            last_name=user.last_name,
            photo=user.photo,
        ),
        settings=dict_settings(users_settings),
        time_offset=user.time_offset,
        mood=dict(
            day=d,
            month=m,
            year=y,
            mood=getMood(user, d, m, y)
        ),
        extraQ=dict(
            day=d,
            month=m,
            year=y,
            extraQ=extraQ
        )
    )

    if extraQ:
        res['extraQ']['question'] = getQuestion(user)

    return res

def dict_moodes(model):
    return dict(
        date=f'{model.year}-{stringNum(model.month)}-{stringNum(model.day)}',
        mood=model.mood
    )

def dict_settings(model):
    return dict(
        notifications=dict(
            app=model.app_notify,
            messages=model.messages_notify
        ),
        extraQ=dict(
            extraQ=model.extraQ,
            unusualExtraQ=model.unusualExtraQ
        ),
        privacy=dict(
            mood_public=model.mood_public,
            profile_button=model.profile_button
        )
    )

def dict_invite(model):
    return dict(
        hash=model.hash,
        book=dict(book_id=model.book.book_id)
    )