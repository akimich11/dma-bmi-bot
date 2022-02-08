import functools
from typing import Literal
import psycopg2
import settings


class ConnectionMixin:
    conn = psycopg2.connect(host=settings.DATABASE_HOST, dbname=settings.DATABASE_NAME,
                            user=settings.DATABASE_USER, password=settings.DATABASE_PASSWORD)
    conn.autocommit = True


def get_cursor(function):
    @functools.wraps(function)
    def wrapped(cls_ref, *args, **kwargs):
        cursor = cls_ref.conn.cursor()
        result = function(cls_ref, *args, **kwargs, cursor=cursor)
        cursor.close()
        return result

    return wrapped


def fetch(return_type: Literal['value', 'tuple', 'all_values', 'all_tuples']):
    def decorator(function):
        @functools.wraps(function)
        def wrapped(cls_ref, *args, **kwargs):
            cursor = cls_ref.conn.cursor()
            function(cls_ref, *args, **kwargs, cursor=cursor)
            data = cursor.fetchone() if return_type in ['value', 'tuple'] else cursor.fetchall()
            cursor.close()
            if return_type in ['tuple', 'all_tuples']:
                return data if data else None
            elif return_type == 'value':
                return data[0] if data is not None else None
            return [el[0] for el in data]

        return wrapped

    return decorator
