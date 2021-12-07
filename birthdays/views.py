import config
from base.bot import bot
from birthdays.utils import get_greetings


def send_greetings(first_name):
    greeting_text = get_greetings(first_name)
    bot.send_message(config.MDA_ID, greeting_text)
