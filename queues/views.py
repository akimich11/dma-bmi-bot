from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from queues.models import queue_model, Queue
from users.models import user_model


@bot.message_handler(commands=['sign_up', 'move'])
@exception_handler
def sign_up(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) == 3:
            command, subject, pos = args
            pos = int(pos)
        elif len(args) == 2:
            command, subject, pos = *args, None
        else:
            raise ValueError()

        user_id = message.from_user.id
        if command == '/sign_up':
            result = queue_model.sign_up(subject, user_id, pos)
        else:
            result = queue_model.move(subject, user_id, pos)
        if result is None:
            resulting_pos = queue_model.queues[subject].positions[user_id]
            bot.send_message(message.chat.id, f'{user_model.users[user_id].first_name} '
                                              f'{user_model.users[user_id].last_name} теперь в очереди '
                                              f'на {subject}, позиция: {resulting_pos}')
        else:
            bot.send_message(message.chat.id, result)
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
        
        
@bot.message_handler(commands=['cancel'])
@exception_handler
def cancel_sign_up(message):
    try:
        command, subject = message.text.split(maxsplit=1)
        user_id = message.from_user.id
        result = queue_model.cancel_sign_up(subject, user_id)
        if result is None:
            bot.send_message(message.chat.id, f'{user_model.users[user_id].first_name} '
                                              f'{user_model.users[user_id].last_name} теперь не в очереди '
                                              f'на {subject}')
        else:
            bot.send_message(message.chat.id, result)
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['queue'])
@exception_handler
def send_queue(message):
    try:
        command, subject = message.text.split(maxsplit=1)
        if subject in queue_model.queues:
            bot.send_message(message.chat.id, str(queue_model.queues[subject]))
        else:
            bot.send_message(message.chat.id, 'Очередь для заданного предмета не найдена :(')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['add_queue'])
@exception_handler
@admin_only
def add_queue(message):
    try:
        command, subject = message.text.split(maxsplit=1)
        queue_model.add_queue(Queue(subject))
        bot.send_message(message.chat.id, 'Очередь создана')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['clear_queue'])
@exception_handler
@admin_only
def clear_queue(message):
    try:
        command, subject = message.text.split(maxsplit=1)
        if queue_model.clear_queue(subject):
            bot.send_message(message.chat.id, 'Очередь очищена')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
