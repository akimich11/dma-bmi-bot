import functools
import mysql.connector
import config


def connector(function):
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
