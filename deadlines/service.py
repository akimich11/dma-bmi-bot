import datetime
from base import db


class DeadlineService(db.ConnectionMixin):
    @classmethod
    @db.fetch(return_type='all_tuples')
    def get_deadlines(cls, user_id, cursor):
        cursor.execute("SELECT name, date FROM deadlines "
                       "WHERE department_id=(SELECT department_id FROM users WHERE id=%s) "
                       "AND date >= %s ORDER BY date", (user_id, datetime.date.today()))
