from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from queues.models import queue_model, Queue
from users.models import user_model


@bot.message_handler(commands=['sign_up', 'move'])
@exception_handler
def sign_up(message):
    try:
        args = message.text.split(maxsplit=3)
        if len(args) == 4:
            command, date, subject, pos = args
            pos = int(pos)
        elif len(args) == 3:
            command, date, subject, pos = *args, None
        else:
            raise ValueError()
            
        user_id = message.from_user.id
        if command == '/sign_up':
            ret = queue_model.sign_up(date, subject, user_id, pos)
        elif command == '/move':
            ret = queue_model.move(date, subject, user_id, pos)
        if ret is None:
            bot.send_message(message.chat.id, f'{user_model.users[user_id].first_name} '
                                              f'{user_model.users[user_id].last_name} теперь в очереди '
                                              f'{date} на {subject}')
        else:
            bot.send_message(message.chat.id, ret)
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
        
        
@bot.message_handler(commands=['cancel'])
@exception_handler
def cancel_sign_up(message):
    try:
        command, date, subject = message.text.split(maxsplit=2)
        user_id = message.from_user.id
        ret = queue_model.cancel_sign_up(date, subject, user_id)
        if ret is None:
            bot.send_message(message.chat.id, f'{user_model.users[user_id].first_name} '
                                              f'{user_model.users[user_id].last_name} теперь не в очереди '
                                              f'{date} на {subject}')
        else:
            bot.send_message(message.chat.id, ret)
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
        bot.send_message(message.chat.id, 'Очередь создана')
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
