import atexit
import settings
from base.bot import bot
from base.db import ConnectionMixin

if __name__ == '__main__':
    bot.send_message(settings.SUPERUSER_ID, 'started')


atexit.register(ConnectionMixin.conn.close)
bot.polling(none_stop=True)
