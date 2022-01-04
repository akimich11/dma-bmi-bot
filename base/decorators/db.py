import functools
from typing import Literal

import mysql.connector
import config


def connect(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        conn = mysql.connector.connect(host=config.HOSTNAME, database=config.DATABASE_NAME,
                                       user=config.USER, password=config.PASSWORD)
        conn.autocommit = True
        cursor = conn.cursor(buffered=True)
        result = function(*args, **kwargs, cursor=cursor)
        cursor.close()
        conn.close()
        return result

    return wrapped


def fetch(return_type: Literal['value', 'tuple', 'all_values', 'all_tuples']):
    def decorator(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            conn = mysql.connector.connect(host=config.HOSTNAME, database=config.DATABASE_NAME,
                                           user=config.USER, password=config.PASSWORD)
            conn.autocommit = True
            cursor = conn.cursor(buffered=True)
            function(*args, **kwargs, cursor=cursor)
            data = cursor.fetchone() if return_type in ['value', 'tuple'] else cursor.fetchall()
            cursor.close()
            conn.close()
            if return_type in ['tuple', 'all_tuples']:
                return data if data else None
            elif return_type == 'value':
                return data[0] if data is not None else None
            return [el[0] for el in data]

        return wrapped

    return decorator
