import config
from base.bot import bot
import skips.views
import polls.views
import users.views
# import queues.views
from schedules.schedule_service import ScheduleService

if __name__ == '__main__':
    ScheduleService.init_schedule()
    bot.send_message(config.AKIM_ID, 'started')

bot.polling(none_stop=True)
