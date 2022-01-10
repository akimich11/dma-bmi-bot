from base.decorators import db
from users.user_service import UserService


class SkipsService:
    @staticmethod
    @db.fetch(return_type='tuple')
    def get_skips(user_id, cursor=None):
        cursor.execute("SELECT skips_month, skips_semester FROM user WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_all_skips(chat_id, cursor=None):
        if chat_id > 0:
            chat_id = UserService.get_group_chat_id(chat_id)
        cursor.execute("SELECT first_name, last_name, skips_month, skips_semester FROM user "
                       "JOIN department ON user.department_id = department.id WHERE chat_id=(%s) "
                       "ORDER BY sub_department DESC, last_name",
                       (chat_id,))

    @staticmethod
    @db.connect
    def set_skips(last_name, skips_month, skips_semester, cursor=None):
        cursor.execute("UPDATE user SET skips_month=(%s), "
                       "skips_semester=(%s) WHERE last_name=(%s)", (skips_month, skips_semester, last_name))

    @staticmethod
    @db.connect
    def inc_skips(last_name_list, cursor=None):
        for last_name in last_name_list:
            cursor.execute("UPDATE user SET skips_month=skips_month+2, "
                           "skips_semester=skips_semester+2 WHERE last_name=(%s)", (last_name,))

    @staticmethod
    @db.connect
    def get_is_skips_cleared(cursor=None):
        cursor.execute("SELECT id FROM user WHERE skips_month != 0 LIMIT 1")
        return cursor.fetchone() is None

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def clear_skips(cursor=None):
        cursor.execute("UPDATE user SET skips_month=0")
        cursor.execute("SELECT name, chat_id FROM department")
