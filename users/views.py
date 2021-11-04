from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from users.models import user_model


@bot.message_handler(commands=['make_admin', 'remove_admin'])
@exception_handler
@admin_only
def set_admin(message):
    try:
        command, last_name = message.text.split()
        is_make_admin = (command == '/make_admin')
        if not user_model.set_admin(last_name, is_make_admin):
            bot.send_message(message.chat.id, 'я такой фамилии не знаю')
        bot.send_message(message.chat.id, f'одним старостой {"больше" if is_make_admin else "меньше"}')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
