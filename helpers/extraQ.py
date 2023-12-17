import math

import peewee

from db.models import QuestionsExtra, Questions
from helpers.time import getCurrentTimestamp, get_utc_timestamp_endday_by_timestamp, \
    get_utc_timestamp_startday_by_timestamp
from datetime import datetime

EQ_timeout_days = 3


def markExtraQ(user, q, d, m, y):
    res = QuestionsExtra.select().where(
        (QuestionsExtra.user == user) &
        (QuestionsExtra.day == d) &
        (QuestionsExtra.month == m) &
        (QuestionsExtra.year == y)
    ).count()

    if res > 0:
        return False

    questions = Questions.select().where(Questions.question==q)
    if len(questions) == 0:
        q_ = QuestionsExtra(
            user=user,
            question=None,
            day=d,
            month=m,
            year=y
        )
    else:
        q_ = QuestionsExtra(
            user=user,
            question=questions[0],
            day=d,
            month=m,
            year=y
        )

    q_.save()
    return True


def extraQreturned(user, d, m, y):
    res = QuestionsExtra.select().where(
        (QuestionsExtra.user == user) &
        (QuestionsExtra.day == d) &
        (QuestionsExtra.month == m) &
        (QuestionsExtra.year == y)
    ).count()

    return res > 0


def needXQ(user, d, m, y):

    if extraQreturned(user, d, m, y):
        return False
    timenow = getCurrentTimestamp()

    if (timenow - user.timestamp_reg) <= (24 * 60 * 60):
        return True

    timestamp_start = get_utc_timestamp_startday_by_timestamp(user.timestamp_reg)
    timestamp_now = get_utc_timestamp_endday_by_timestamp(timenow)
    d_time = timestamp_now - timestamp_start
    d_time_days = int(round(d_time / 60 / 60 / 24))

    if d_time_days <= 1:
        return True

    if d_time_days % EQ_timeout_days == 0:
        return True

    return False

def getTypeQuestion(unusuals, i):
    if i in [1,2,5,7,8,10]:
        return 'default'

    if i in [3,9]:
        return 'disposable'

    if i in [4,5,6]:
        if unusuals:
            return 'unusual'

        if i == 5:
            return 'disposable'
        else:
            return 'default'

def returnQuestion(user, i, type):
    if type == 'default':
        question = Questions.select().where((Questions.day_index == i) & (Questions.type=='default')).order_by(Questions.uses.asc()).limit(1)

    if type == 'unusual':
        question = Questions.select().where((Questions.day_index == i) & (Questions.type == 'unusual')).order_by(
            Questions.uses.asc()).limit(1)

    if type == 'disposable':
        disposables = Questions.select().where(Questions.type=='disposable')
        print(len(disposables))
        disposables_answer = QuestionsExtra.select().where((QuestionsExtra.user==user) & (QuestionsExtra.question.in_(disposables)))
        access = list(set([qe.id for qe in disposables]) - set([qe.question.id for qe in disposables_answer]))
        print(access)
        disposables_noanswer = Questions.select().where(Questions.id.in_(access))
        if len(disposables_noanswer) == 0:
            question = Questions.select().where((Questions.day_index == i) & (Questions.type == 'default')).order_by(
                Questions.uses.asc()).limit(1)
        else:
            question = [disposables_noanswer[0]]
    return question

def getQuestion(user):
    try:
        w_day = datetime.now().isoweekday()
        answers_count = QuestionsExtra.select().where(QuestionsExtra.user == user).count()
        index = ((answers_count)%10) + 1
        w_index = ((answers_count+w_day)%10) + 1
        q_type = getTypeQuestion(user.settings[0].unusualExtraQ, index)
        # question = Questions.select().where(Questions.day_index == w_index).order_by(Questions.uses.asc()).limit(1)
        question = returnQuestion(user, w_index, q_type)
        if len(question) == 0:
            return dict(
                question='С чего вы сегодня хорошо посмеялись?',
                description=''
            )
        return dict(
            question=question[0].question,
            description=question[0].description
        )
    except:
        return dict(
            question='С чего вы сегодня хорошо посмеялись?',
            description='*'
        )