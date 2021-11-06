from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from queues.models import queue_model, Queue
from users.models import user_model


@bot.message_handler(commands=['sign_up', 'move'])
@exception_handler
def sign_up(message):
    try:
        command, subject, pos = _parse_args(message.text, with_pos=True)
        user_id = message.from_user.id
        if command == '/sign_up':
            result = queue_model.sign_up(subject, user_id, pos)
        else:
            result = queue_model.move(subject, user_id, pos)
        if result is None:
            subject = subject or queue_model.last_queue
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
        command, subject = _parse_args(message.text)
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
        command, subject = _parse_args(message.text)
        queue_str = queue_model.get_queue(subject)
        if queue_str is not None:
            bot.send_message(message.chat.id, queue_str)
        else:
            bot.send_message(message.chat.id, 'Очередь для заданного предмета не найдена :(')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
        
@bot.message_handler(commands=['queues'])
@exception_handler
def send_queue(message):
    bot.send_message(message.chat.id,
                     'Вот они слева направо:\n' + queue_model.get_all_queues())


@bot.message_handler(commands=['add_queue'])
@exception_handler
@admin_only
def add_queue(message):
    try:
        command, subject = message.text.split(maxsplit=1)
        if _can_convert_to_int(subject):
            bot.send_message(message.chat.id, 'Не умею называть очереди числами :(')
        elif ' ' in subject:
            bot.send_message(message.chat.id, 'Ограничьте свою фантазию одним словом')
        else:
            queue_model.add_queue(Queue(subject))
            bot.send_message(message.chat.id, 'Очередь создана')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['clear_queue'])
@exception_handler
@admin_only
def clear_queue(message):
    try:
        command, subject = _parse_args(text.message)
        if queue_model.clear_queue(subject):
            bot.send_message(message.chat.id, 'Очередь очищена')
        else:
            bot.send_message(message.chat.id, 'Что-то не вышло(')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')
        
def _can_convert_to_int(s):
    answer = False
    try:
        int(s)
        answer = True
    except ValueError:
        pass
    return answer
    
def _parse_args(text, with_pos=False):
    args = text.split(maxsplit=(2 if with_pos else 1))
    command = args[0]
    subject = None
    pos = None
    for arg in args[1:]:
        if not _can_convert_to_int(arg):
            subject = arg
        elif with_pos:
            pos = int(arg)
        else:
            raise ValueError()
            
    if with_pos:
        return command, subject, pos
    else:
        return command, subject
