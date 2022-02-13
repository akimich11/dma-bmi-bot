from base.bot import bot
from base.decorators import access_checker
from deadlines.service import DeadlineService


@bot.message_handler(commands=['deadlines'])
@access_checker(admin_only=False)
def send_deadlines(message):
    deadlines = DeadlineService.get_deadlines(message.from_user.id)
    bot.send_message(message.chat.id, '\n'.join([f'{date:%d.%m} {name}' for name, date in deadlines]))
