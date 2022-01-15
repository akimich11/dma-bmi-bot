from base.bot import bot


@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    bot.send_message(message.chat.id, message.chat.id)
