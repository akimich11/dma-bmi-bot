import settings
from base.bot import bot


if __name__ == '__main__':
    bot.send_message(settings.SUPERUSER_ID, 'started')


bot.polling(none_stop=True)
