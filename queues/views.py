from base.bot import bot
from base.decorators.common import exception_handler


@bot.message_handler(commands=['sign_up'])
@exception_handler
def sign_up(message):
    pass


@bot.message_handler(commands=['queue'])
@exception_handler
def sign_up(message):
    pass
