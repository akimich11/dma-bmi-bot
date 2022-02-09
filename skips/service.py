from base import db


class SkipsService(db.ConnectionMixin):
    @classmethod
    @db.fetch(return_type='tuple')
    def get_skips(cls, user_id, cursor):
        cursor.execute("SELECT skips_month, skips_semester FROM users WHERE id=(%s)", (user_id,))

    @classmethod
    @db.fetch(return_type='all_tuples')
    def get_all_skips(cls, chat_id, cursor):
        cursor.execute("SELECT first_name, last_name, skips_month, skips_semester FROM users "
                       "JOIN departments ON users.department_id = departments.id WHERE chat_id=(%s) "
                       "ORDER BY sub_department DESC, last_name",
                       (chat_id,))

    @classmethod
    @db.get_cursor
    def set_skips(cls, last_name, skips_month, skips_semester, cursor):
        cursor.execute("UPDATE users SET skips_month=(%s), "
                       "skips_semester=(%s) WHERE last_name=(%s)", (skips_month, skips_semester, last_name))

    @classmethod
    @db.get_cursor
    def inc_skips(cls, last_name_list, cursor):
        for last_name in last_name_list:
            cursor.execute("UPDATE users SET skips_month=skips_month+2, "
                           "skips_semester=skips_semester+2 WHERE last_name=(%s)", (last_name,))

    @classmethod
    @db.get_cursor
    def get_is_skips_cleared(cls, cursor):
        cursor.execute("SELECT id FROM users WHERE skips_month != 0 LIMIT 1")
        return cursor.fetchone() is None

    @classmethod
    @db.fetch(return_type='all_tuples')
    def clear_skips(cls, cursor):
        cursor.execute("UPDATE users SET skips_month=0")
        cursor.execute("SELECT name, chat_id FROM departments")
