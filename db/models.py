from peewee import *

#
# db = PostgresqlDatabase('tester', user='tester',
#                             host='localhost', port=5432)

db = SqliteDatabase('./db_track.sqlite')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    vk_id = BigIntegerField(unique=True)
    first_name = CharField(null=True, max_length=100)
    last_name = CharField(null=True, max_length=100)
    photo = TextField(null=True)
    timestamp_reg = BigIntegerField()
    timestamp_vk_reload = BigIntegerField()
    time_offset = FloatField(default=0)

class Settings(BaseModel):
    user = ForeignKeyField(User, backref='settings')

    app_notify = BooleanField(default=False)
    messages_notify = BooleanField(default=False)

    extraQ = BooleanField(default=True)
    unusualExtraQ = BooleanField(default=False)

    mood_public = BooleanField(default=False)
    profile_button = BooleanField(default=False)

class Diary(BaseModel):
    book_id = CharField(max_length=50)
    author = ForeignKeyField(User, backref='books')
    mode = CharField(max_length=10, default='person')
    name = CharField(max_length=50)
    description = CharField(max_length=500)
    timestamp_create = BigIntegerField()


class Post(BaseModel):
    post_id = CharField(unique=True, max_length=50)
    book = ForeignKeyField(Diary, backref='posts')
    author = ForeignKeyField(User, backref='posts')
    text = TextField()
    extra_content = TextField(null=True)

    timestamp_create = BigIntegerField()
    day = IntegerField(null=True)
    month = IntegerField(null=True)
    year = IntegerField(null=True)
    timestamp_thisday = BigIntegerField()


class Member(BaseModel):
    book = ForeignKeyField(Diary, backref='members')
    member = ForeignKeyField(User, backref='members')
    mode = CharField(max_length=20, default='read')
    timestamp_join = BigIntegerField()


class Invite(BaseModel):
    book = ForeignKeyField(Diary, backref='invites')
    author = ForeignKeyField(User)
    hash = CharField(max_length=100)
    timestamp_border = TimestampField(default=9999999999)
    openplaces = IntegerField(default=1)


class Attachment(BaseModel):
    attachment_id = CharField(unique=True, max_length=50)
    author = ForeignKeyField(User)
    post = ForeignKeyField(Post, backref='attachments', null=True)
    type = CharField(max_length=20)
    content = TextField(null=True)


class Moodes(BaseModel):
    user = ForeignKeyField(User, backref='moodes')
    day = IntegerField()
    month = IntegerField()
    year = IntegerField()
    timestamp_thisday = IntegerField(null=True)
    timestamp_create = IntegerField()
    mood = IntegerField(null=True)


class Questions(BaseModel):
    question = TextField()
    description = TextField(default='')
    type = CharField(max_length=30, default='default')
    day_index = IntegerField()
    uses = IntegerField(default=0)

class QuestionsExtra(BaseModel):
    user = ForeignKeyField(User)
    question = ForeignKeyField(Questions, null=True)
    day = IntegerField()
    month = IntegerField()
    year = IntegerField()

class UploadedImages(BaseModel):
    user = ForeignKeyField(User)
    timestamp = IntegerField()
    url = TextField()


db.connect()
db.create_tables([User, Diary, Invite, Member, Post,
                  Attachment, Moodes,
                  Questions, QuestionsExtra, Settings, UploadedImages])
