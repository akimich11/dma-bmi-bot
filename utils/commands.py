import settings
from base.bot import bot


@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(commands=['register'])
def register_user(message):
    user_data = '\n'.join([f'id: {message.from_user.id}',
                           f'username: @{message.from_user.username}',
                           f'first_name: {message.from_user.first_name}',
                           f'last_name: {message.from_user.last_name}']
                          )
    bot.send_message(settings.AKIM_ID, user_data)
