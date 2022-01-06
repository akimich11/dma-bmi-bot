# from threading import Thread

import config
# import schedule
from base.bot import bot
# from schedules.utils import send_periodic_question, schedule_check, get_questions
import skips.views
import polls.views
import users.views
# import queues.views


if __name__ == '__main__':
    # questions = get_questions()
    # for question in questions:
    #     getattr(schedule.every(), question.weekday
    #             ).at(question.time).do(send_periodic_question, question=question)
    #
    # Thread(target=schedule_check).start()
    bot.send_message(config.AKIM_ID, 'started')

bot.polling(none_stop=True)
