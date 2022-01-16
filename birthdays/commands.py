from base.bot import bot
from birthdays.service import get_greetings, BirthdayService


def send_greetings(chat_id, first_name, last_name):
    greeting_text = get_greetings(first_name)
    BirthdayService.update_next_birthday(last_name)
    bot.send_message(chat_id, greeting_text)
