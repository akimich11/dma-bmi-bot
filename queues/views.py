from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from queues import status
from queues.models import queue_model, Queue
from users.models import user_model


@bot.message_handler(commands=['sign_up', 'move'])
@exception_handler
def sign_up(message):
    res_name, res_pos = None, None
    user_id = message.from_user.id
    status.handler.success_msg = '{} {} теперь в очереди на {}, позиция: {}'

    try:
        command, name, pos = _parse_args(message.text, with_pos=True)
        if command.startswith('/sign_up'):
            res_name, res_pos = queue_model.sign_up(name, user_id, pos)
        else:
            res_name, res_pos = queue_model.move(name, user_id, pos)
    except ValueError:
        status.handler.error(status.VALUE_ERROR)

    status.handler.send_and_reset(message.chat.id, success_args=[
        user_model.users[user_id].first_name,
        user_model.users[user_id].last_name,
        res_name,
        res_pos,
    ])


@bot.message_handler(commands=['cancel', 'shift'])
@exception_handler
def cancel_sign_up(message):
    res_name = None
    user_id = message.from_user.id
    status.handler.success_msg = '{} {} теперь не в очереди на {}'
    try:
        command, name = _parse_args(message.text)
        res_name = queue_model.cancel_sign_up(name, user_id, is_shift=command == 'shift')
    except ValueError:
        status.handler.error(status.VALUE_ERROR)

    status.handler.send_and_reset(message.chat.id, success_args=[
        user_model.users[user_id].first_name,
        user_model.users[user_id].last_name,
        res_name,
    ])


@bot.message_handler(commands=['queue'])
@exception_handler
def send_queue(message):
    queue_str = None
    status.handler.success_msg = '{}'
    try:
        command, name = _parse_args(message.text)
        queue_str = queue_model.get_queue(name)
    except ValueError:
        status.handler.error(status.VALUE_ERROR)

    status.handler.send_and_reset(message.chat.id, success_args=[queue_str])


@bot.message_handler(commands=['queues'])
@exception_handler
def send_queues(message):
    bot.send_message(message.chat.id,
                     ('Как же я люблю очереди, вот они слева направо:\n'
                      + queue_model.get_all_queues()))


@bot.message_handler(commands=['add_queue'])
@exception_handler
@admin_only
def add_queue(message):
    status.handler.success_msg = 'Очередь создана'
    try:
        command, name = message.text.split(maxsplit=1)
        if _can_convert_to_int(name):
            status.handler.error('Не умею называть очереди числами :(')
        elif ' ' in name:
            status.handler.error('Ограничьте свою фантазию одним словом')
        else:
            queue_model.add_queue(Queue(name.lower().capitalize()))
    except ValueError:
        status.handler.error(status.VALUE_ERROR)

    status.handler.send_and_reset(message.chat.id)


@bot.message_handler(commands=['clear_queue'])
@exception_handler
@admin_only
def clear_queue(message):
    status.handler.success_msg = 'Очередь очищена'
    try:
        command, name = _parse_args(message.text)
        queue_model.clear_queue(name)
    except ValueError:
        status.handler.error(status.VALUE_ERROR)

    status.handler.send_and_reset(message.chat.id)


@bot.message_handler(commands=['remove_queue'])
@exception_handler
@admin_only
def remove_queue(message):
    status.handler.success_msg = 'Очередь удалена'
    try:
        command, name = _parse_args(message.text)
        queue_model.remove_queue(name)
    except ValueError:
        status.handler.error(status.VALUE_ERROR)

    status.handler.send_and_reset(message.chat.id)


def _can_convert_to_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def _parse_args(text, with_pos=False):
    args = text.split(maxsplit=(2 if with_pos else 1))

    command = args[0]
    name, pos = None, None
    for arg in args[1:]:
        if not _can_convert_to_int(arg):
            name = arg.lower().capitalize()
        elif with_pos:
            pos = int(arg)
        else:
            raise ValueError()

    if with_pos:
        return command, name, pos
    else:
        return command, name
