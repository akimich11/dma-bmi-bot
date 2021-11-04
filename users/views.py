from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from users.models import user_model


@bot.message_handler(commands=['make_admin'])
@exception_handler
@admin_only
def make_admin(message):
    try:
        command, last_name = message.text.split()
        if user_model.make_admin(last_name):
            bot.send_message(message.chat.id, 'одним старостой больше')
        else:
            bot.send_message(message.chat.id, 'я такой фамилии не знаю')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['remove_admin'])
@exception_handler
@admin_only
def remove_admin(message):
    try:
        command, last_name = message.text.split()
        if user_model.remove_admin(last_name):
            bot.send_message(message.chat.id, 'одним старостой меньше')
        else:
            bot.send_message(message.chat.id, 'я такой фамилии не знаю')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
