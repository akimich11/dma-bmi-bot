import functools
import mysql.connector
import config


def connector(function):
    @functools.wraps(function)
    def wrapped(self, *args, **kwargs):
        self.conn = mysql.connector.connect(host=config.HOSTNAME, database=config.DATABASE_NAME,
                                            user=config.USER, password=config.PASSWORD)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(buffered=True)
        result = function(self, *args, **kwargs)
        self.cursor.close()
        self.conn.close()
        return result
    return wrapped
