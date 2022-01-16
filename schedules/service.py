import time
from datetime import datetime

import schedule
from threading import Thread, Timer

from base.bot import bot
from base.decorators import db
from base.decorators.common import exception_handler
from birthdays.service import BirthdayService
from birthdays.commands import send_greetings
from skips.service import SkipsService
from skips.commands import clear_skips


class ScheduleService:
    @staticmethod
    @exception_handler
    def schedule_check():
        while True:
            schedule.run_pending()
            time.sleep(30)

    @staticmethod
    @exception_handler
    def send_periodic_question(question, is_multi, chat_id):
        bot.send_poll(chat_id=chat_id,
                      question=f'{question} {datetime.utcnow().day}.{datetime.utcnow().month}',
                      options=['да', 'нет'],
                      is_anonymous=False,
                      allows_multiple_answers=is_multi
                      )

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_scheduled_polls(cursor=None):
        cursor.execute("SELECT question, utc_time, weekday, is_multi, chat_id FROM scheduled_polls "
                       "JOIN departments d on d.id = scheduled_polls.department_id")

    @staticmethod
    def init_skips():
        now = datetime.utcnow()
        if now.day == 1 and SkipsService.get_is_skips_cleared():
            clear_skips()

    @staticmethod
    def init_schedule():
        ScheduleService.init_skips()
        scheduled_polls = ScheduleService.get_scheduled_polls()
        birthdays = BirthdayService.get_all_birthdays()
        if scheduled_polls is not None:
            for question, send_time, weekday, is_multi, chat_id in scheduled_polls:
                getattr(schedule.every(), weekday).at(send_time).do(ScheduleService.send_periodic_question,
                                                                    question=question,
                                                                    chat_id=chat_id,
                                                                    is_multi=is_multi)
        if birthdays is not None:
            for birthday_date, first_name, last_name, chat_id in birthdays:
                delay = (birthday_date - datetime.now()).total_seconds()
                Timer(delay, send_greetings, args=(chat_id, first_name, last_name)).start()
        thread = Thread(target=ScheduleService.schedule_check)
        thread.daemon = True
        thread.start()
