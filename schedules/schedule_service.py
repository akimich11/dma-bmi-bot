import time
from datetime import datetime

import schedule
from threading import Thread, Timer

from base.bot import bot
from base.decorators import db
from base.decorators.common import exception_handler
from birthdays.views import send_greetings
from skips.periodic import check_and_clear_skips
from users.db import UserService


@exception_handler
def schedule_check():
    is_cleared = False
    while True:
        schedule.run_pending()
        is_cleared = check_and_clear_skips(is_cleared)
        time.sleep(30)


@exception_handler
def send_periodic_question(question, is_multi, chat_id):
    bot.send_poll(chat_id=chat_id,
                  question=f'{question} {datetime.utcnow().day}.{datetime.utcnow().month}',
                  options=['да', 'нет'],
                  is_anonymous=False,
                  allows_multiple_answers=is_multi
                  )


@db.fetch(return_type='all_tuples')
def get_questions(cursor=None):
    cursor.execute("SELECT question, `utc_time`, weekday, is_multi, chat_id FROM poll_schedule "
                   "JOIN department d on d.id = poll_schedule.department_id")


def init_schedule():
    questions = get_questions()
    birthdays = UserService.get_birthdays()
    for question_text, question_time, weekday, is_multi, chat_id in questions:
        getattr(schedule.every(), weekday).at(question_time).do(send_periodic_question,
                                                                question=question_text,
                                                                chat_id=chat_id,
                                                                is_multi=is_multi)
    for birthday_date, first_name, last_name in birthdays:
        delay = (birthday_date - datetime.now()).total_seconds()
        Timer(delay, send_greetings, args=(first_name, last_name))
    Thread(target=schedule_check).start()
