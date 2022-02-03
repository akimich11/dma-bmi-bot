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
            res_name, res_pos = QueueService.move(message.chat.id, name, user_id, pos)
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
    user_id = message.from_user.id
    try:
        command, name = _parse_args(message.text)
        res_name = QueueService.cancel_sign_up(message.chat.id, name, user_id,
                                              is_shift=command.startswith('/self_shift'))
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    first_name, last_name = UserService.get_name(user_id)
    bot.send_message(message.chat.id,
        f'{first_name} {last_name} теперь не в очереди на {res_name}')


@bot.message_handler(commands=['shift_queue'])
@exception_handler
@access_checker(admin_only=True)
@queue_exception_handler
def shift_first(message):
    try:
        _, name = _parse_args(message.text)
        res_name, user_id = QueueService.shift_first(message.chat.id, name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    first_name, last_name = UserService.get_name(user_id)
    bot.send_message(message.chat.id,
        f'{first_name} {last_name} теперь не в очереди на {res_name}')


@bot.message_handler(commands=['queue'])
@exception_handler
@access_checker(admin_only=False)
@queue_exception_handler
def send_queue(message):
    try:
        _, name = _parse_args(message.text)
        res_name, queue_data = QueueService.get_queue_data(message.chat.id, name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    if queue_data is None or not queue_data:
        bot.send_message(message.chat.id,
                         f'{res_name}. Очередь пока пустая, занимай пока не поздно')
    else:
        queue_rows = []
        for i, user_id in queue_data:
            first_name, last_name = UserService.get_name(user_id)
            queue_rows.append(f'{i}. {first_name} {last_name}')
        bot.send_message(message.chat.id,
            f'{res_name}\nОчередь:\n' + '\n'.join(queue_rows))


@bot.message_handler(commands=['queues'])
@exception_handler
@access_checker(admin_only=False)
@queue_exception_handler
def send_queues(message):
    queues = QueueService.get_all_queues(message.chat.id)
    queues_str = '\n'.join([f'{i + 1}. {name}' for i, name in enumerate(queues)])
    bot.send_message(message.chat.id,
                     f'Как же я люблю очереди, вот они слева направо:\n{queues_str}')


@bot.message_handler(commands=['add_queue'])
@exception_handler
@access_checker(admin_only=True)
@queue_exception_handler
def add_queue(message):
    try:
        _, name = message.text.split(maxsplit=1)
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
@queue_exception_handler
def clear_queue(message):
    try:
        _, name = _parse_args(message.text)
        QueueService.clear_queue(message.chat.id, name)
    except ValueError:
        raise QueueException(VALUE_ERROR_MSG)

    bot.send_message(message.chat.id, 'Очередь очищена')


@bot.message_handler(commands=['remove_queue'])
@exception_handler
@access_checker(admin_only=True)
@queue_exception_handler
def remove_queue(message):
    try:
        _, name = _parse_args(message.text)
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
