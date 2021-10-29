from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from queues.models import queue_model, Queue


@bot.message_handler(commands=['sign_up'])
@exception_handler
def sign_up(message):
    try:
        command, date, subject = message.text.split(maxsplit=2)
        user_id = message.from_user.id
        if queue_model.sign_up(date, subject, user_id):
            bot.send_message(user_id, 'Добавил тебя в очередь.\n'
                                      f'предмет: {subject}, дата: {date}',
                             reply_to_message_id=message.id)
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['queue'])
@exception_handler
def send_queue(message):
    try:
        command, date, subject = message.text.split(maxsplit=2)
        if (date, subject) in queue_model.queues:
            bot.send_message(message.chat.id, str(queue_model.queues[(date, subject)]))
        else:
            bot.send_message(message.chat.id, 'Очередь для заданных предмета и даты не найдена :(')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['add_queue'])
@exception_handler
@admin_only
def add_queue(message):
    try:
        command, date, subject = message.text.split(maxsplit=2)
        queue_model.add_queue(Queue(date=date, subject=subject))
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['clear_queue'])
@exception_handler
@admin_only
def clear_queue(message):
    try:
        command, date, subject = message.text.split(maxsplit=3)
        if queue_model.clear_queue(date, subject):
            bot.send_message(message.chat.id, 'Очередь очищена')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
