import functools
from base.bot import bot


class QueueException(Exception):
    pass


def queue_exception_handler(function):
    @functools.wraps(function)
    def wrapped(message, *args, **kwargs):
        try:
            result = function(message, *args, **kwargs)
            return result
        except QueueException as e:
            bot.send_message(message.chat.id, e)
            return None

    return wrapped
