import time
from datetime import datetime

import schedule
from threading import Thread, Timer

from base.bot import bot
from base import db
from base.decorators import exception_handler
from birthdays.service import BirthdayService
from birthdays.commands import send_greetings
from polls.service import PollService
from skips.service import SkipsService
from skips.commands import clear_skips


class ScheduleService(db.ConnectionMixin):
    @staticmethod
    @exception_handler
    def schedule_check():
        while True:
            schedule.run_pending()
            time.sleep(30)

    @staticmethod
    @exception_handler
    def send_periodic_question(question, is_multi, chat_id):
        options = PollService.get_options_by_scheduled_poll_question(chat_id, question)
        bot.send_poll(group_chat_id=chat_id,
                      question=f'{question} {datetime.utcnow().day:0>2}.{datetime.utcnow().month:0>2}',
                      options=options or ['да', 'нет'],
                      is_anonymous=False,
                      allows_multiple_answers=is_multi
                      )

    @classmethod
    @db.fetch(return_type='all_tuples')
    def get_scheduled_polls(cls, cursor):
        cursor.execute("SELECT question, utc_time, weekday, is_multi, chat_id FROM scheduled_polls "
                       "JOIN departments d on d.id = scheduled_polls.department_id")

    @staticmethod
    def init_skips():
        now = datetime.utcnow()
        if now.day == 1 and SkipsService.get_is_skips_cleared():
            clear_skips()

    @classmethod
    def init_schedule(cls):
        cls.init_skips()
        scheduled_polls = cls.get_scheduled_polls()
        birthdays = BirthdayService.get_all_birthdays()
        if scheduled_polls is not None:
            for question, send_time, weekday, is_multi, chat_id in scheduled_polls:
                getattr(schedule.every(), weekday).at(f'{send_time:%H:%M}').do(ScheduleService.send_periodic_question,
                                                                               question=question,
                                                                               chat_id=chat_id,
                                                                               is_multi=is_multi)
        if birthdays is not None:
            for birthday_date, first_name, last_name, chat_id in birthdays:
                delay = (birthday_date - datetime.now()).total_seconds()
                timer = Timer(delay, send_greetings, args=(chat_id, first_name, last_name))
                timer.daemon = True
                timer.start()
        thread = Thread(target=ScheduleService.schedule_check)
        thread.daemon = True
        thread.start()
