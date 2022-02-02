from base.bot import bot
from base.decorators.common import exception_handler, access_checker
from users.service import UserService


@bot.message_handler(commands=['make_admin', 'remove_admin'])
@exception_handler
@access_checker(admin_only=True)
def set_admin(message):
    try:
        command, last_name = message.text.split()
        is_make_admin = (command == '/make_admin')
        UserService.set_admin(last_name, is_make_admin)
        bot.send_message(message.chat.id, f'одним старостой {"больше" if is_make_admin else "меньше"}')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
