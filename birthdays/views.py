import config
from base.bot import bot
from birthdays.utils import get_greetings
from users.db import UserService


def send_greetings(first_name, last_name):
    greeting_text = get_greetings(first_name)
    UserService.update_next_birthday(first_name, last_name)
    bot.send_message(config.MDA_ID, greeting_text)

