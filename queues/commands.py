from base.bot import bot
from base.decorators.common import exception_handler, access_checker
from queues.errors import QueueException, queue_exception_handler
from queues.service import QueueService
from users.service import UserService

VALUE_ERROR_MSG = 'Не тот формат :('


@bot.message_handler(commands=['sign_up', 'move'])
@exception_handler
@access_checker(admin_only=False)
@queue_exception_handler
def sign_up(message):
    user_id = message.from_user.id
    try:
        command, name, pos = _parse_args(message.text, with_pos=True)
        if command.startswith('/sign_up'):
            res_name, res_pos = QueueService.sign_up(message.chat.id, name, user_id, pos)
        else:
            res_name, res_pos = queue_model.move(message.chat.id, name, user_id, pos)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    first_name, last_name = UserService.get_name(user_id)
    bot.send_message(message.chat.id,
        f'{first_name} {last_name} теперь в очереди на {res_name}, позиция: {res_pos}')

@bot.message_handler(commands=['cancel', 'self_shift'])
@exception_handler
@access_checker(admin_only=False)
@queue_exception_handler
def cancel_sign_up(message):
    res_name = None
    user_id = message.from_user.id
    status.handler.success_msg = '{} {} теперь не в очереди на {}'
    try:
        command, name = _parse_args(message.text)
        res_name = queue_model.cancel_sign_up(name, user_id,
                                              is_shift=command.split('@')[0] == '/self_shift')
        if res_name is None:
            raise ValueError
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    status.handler.send_and_reset(message.chat.id, success_args=[
        user_model.users[user_id].first_name,
        user_model.users[user_id].last_name,
        res_name,
    ])


@bot.message_handler(commands=['shift_queue'])
@exception_handler
@access_checker(admin_only=True)
def shift_first(message):
    queue_name, first_name, last_name = None, None, None
    status.handler.success_msg = '{} {} теперь не в очереди на {}'
    try:
        command, name = _parse_args(message.text)
        queue_name, first_name, last_name = queue_model.shift_queue(name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    status.handler.send_and_reset(message.chat.id, success_args=[
        first_name,
        last_name,
        queue_name,
    ])


@bot.message_handler(commands=['queue'])
@exception_handler
@access_checker(admin_only=False)
def send_queue(message):
    queue_str = None
    status.handler.success_msg = '{}'
    try:
        command, name = _parse_args(message.text)
        queue_str = queue_model.get_queue(name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    status.handler.send_and_reset(message.chat.id, success_args=[queue_str])


@bot.message_handler(commands=['queues'])
@exception_handler
@access_checker(admin_only=False)
def send_queues(message):
    bot.send_message(message.chat.id,
                     ('Как же я люблю очереди, вот они слева направо:\n'
                      + queue_model.get_all_queues()))


@bot.message_handler(commands=['add_queue'])
@exception_handler
@access_checker(admin_only=True)
@queue_exception_handler
def add_queue(message):
    try:
        command, name = message.text.split(maxsplit=1)
        if _can_convert_to_int(name):
            raise QueueException('Не умею называть очереди числами :(')
        elif ' ' in name:
            raise QueueException('Ограничьте свою фантазию одним словом')
        else:
            QueueService.create_queue(message.chat.id, name.lower().capitalize())
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    bot.send_message(message.chat.id, 'Очередь создана')


@bot.message_handler(commands=['clear_queue'])
@exception_handler
@access_checker(admin_only=True)
def clear_queue(message):
    status.handler.success_msg = 'Очередь очищена'
    try:
        command, name = _parse_args(message.text)
        queue_model.clear_queue(name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    status.handler.send_and_reset(message.chat.id)


@bot.message_handler(commands=['remove_queue'])
@exception_handler
@access_checker(admin_only=True)
@queue_exception_handler
def remove_queue(message):
    try:
        command, name = _parse_args(message.text)
        QueueService.remove_queue(message.chat.id, name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    bot.send_message(message.chat.id, 'Очередь удалена')


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
