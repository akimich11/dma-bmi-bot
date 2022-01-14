import functools
import traceback

import config
from base.bot import bot
from users.user_service import UserService


def access_checker(admin_only=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(message, *args, **kwargs):
            is_admin = UserService.get_is_admin(message.from_user.id)
            if (admin_only and is_admin) or (not admin_only and is_admin is not None):
                return func(message, *args, **kwargs)
            elif is_admin is None:
                bot.send_message(message.chat.id, 'Вас нет в базе, функционал бота недоступен')
            else:
                bot.send_message(message.chat.id, 'Команда доступна только старостам')
        return wrapped
    return decorator


def exception_handler(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except BaseException:
            bot.send_message(config.AKIM_ID, 'Unexpected error:\n' + traceback.format_exc())
            if len(args):
                if hasattr(args[0], 'message'):
                    chat_id = args[0].message.chat.id
                else:
                    chat_id = args[0].chat.id
                bot.send_message(chat_id, 'Unexpected error')
            return None
    return wrapped
