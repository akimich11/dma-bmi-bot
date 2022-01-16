import settings
from base.bot import bot
import skips.commands
import polls.commands
import users.commands
import utils.commands
# import queues.views
from schedules.service import ScheduleService

if __name__ == '__main__':
    ScheduleService.init_schedule()
    bot.send_message(settings.AKIM_ID, 'started')

bot.polling(none_stop=True)
