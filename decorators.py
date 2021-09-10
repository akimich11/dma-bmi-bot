import functools
import config


def admin_only(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        if message.from_user.id == config.AKIM_ID:
            return func(message, *args, **kwargs)
    return wrapped
