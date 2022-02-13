import atexit
import settings
from base.bot import bot
from base.db import ConnectionMixin
from schedules.service import ScheduleService


if __name__ == '__main__':
    ScheduleService.init_schedule()
    bot.send_message(settings.SUPERUSER_ID, 'started')


atexit.register(ConnectionMixin.conn.close)
bot.polling(none_stop=True)
