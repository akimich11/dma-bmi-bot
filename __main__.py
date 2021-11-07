from datetime import datetime
import time
from threading import Thread

import config
import schedule
from base.bot import bot
from base.decorators.common import exception_handler
from schedules.models import QuestionModel
import skips.views
import polls.views
import users.views
import queues.views


@exception_handler
def schedule_check():
    cleared = False
    while True:
        schedule.run_pending()
        now = datetime.utcnow()
        today_midnight = now.replace(hour=0, minute=2, second=0, microsecond=0)
        if now.day == 1 and now < today_midnight and not cleared:
            skips.views.clear_skips()
            cleared = True
        if now.day == 2:
            cleared = False
        time.sleep(30)


@exception_handler
def send_periodic_question(question):
    bot.send_poll(chat_id=config.MDA_ID,
                  question=f'{question.question} {datetime.utcnow().day}.{datetime.utcnow().month}',
                  options=question.options,
                  is_anonymous=False,
                  allows_multiple_answers=question.is_multi
                  )


if __name__ == '__main__':
    for q in QuestionModel().questions:
        getattr(schedule.every(), q.weekday
                ).at(q.time).do(send_periodic_question, question=q)

    Thread(target=schedule_check).start()
    bot.send_message(config.AKIM_ID, 'started')

bot.polling(none_stop=True)
