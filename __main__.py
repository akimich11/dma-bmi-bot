import config
# import schedule
from base.bot import bot
# from schedules.utils import send_periodic_question, schedule_check, get_questions
import skips.views
import polls.views
import users.views
# import queues.views
from schedules.schedule_service import init_schedule

if __name__ == '__main__':
    init_schedule()
    bot.send_message(config.AKIM_ID, 'started')

bot.polling(none_stop=True)
