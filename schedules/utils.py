import time
from datetime import datetime

import schedule

import config
from base.bot import bot
from base.decorators.common import exception_handler
from base.decorators.db import connector
from base.models import Question
from birthdays.periodic import check_birthdays
from skips.periodic import check_and_clear_skips


@exception_handler
def schedule_check():
    is_cleared = False
    while True:
        schedule.run_pending()
        is_cleared = check_and_clear_skips(is_cleared)
        check_birthdays()
        time.sleep(30)


@exception_handler
def send_periodic_question(question):
    bot.send_poll(chat_id=config.MDA_ID,
                  question=f'{question.question} {datetime.utcnow().day}.{datetime.utcnow().month}',
                  options=question.options,
                  is_anonymous=False,
                  allows_multiple_answers=question.is_multi
                  )


@connector
def get_questions(cursor=None):
    cursor.execute("""SELECT * FROM question""")
    data = cursor.fetchall()
    questions = []
    column_names = [column[0] for column in cursor.description]
    if data is not None:
        for row in data:
            questions.append(Question(**dict(zip(column_names, row))))
    return questions
