import functools
import traceback

import config
from base.bot import bot
from users.models import user_model


def admin_only(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        user = user_model.users.get(message.from_user.id)
        if user is not None and user.is_admin:
            return func(message, *args, **kwargs)
        else:
            bot.send_message(message.chat.id, 'Команда доступна только старостам')
    return wrapped


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
