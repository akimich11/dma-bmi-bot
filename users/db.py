from base.decorators import db

# todo: проверки на деда


class UserService:
    @staticmethod
    @db.fetch(return_type='tuple')
    def get_skips(user_id, cursor=None):
        cursor.execute("SELECT skips_month, skips_semester FROM user WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_is_admin(user_id, cursor=None):
        cursor.execute("SELECT is_admin FROM user WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_group_chat_id(user_id, cursor=None):
        cursor.execute("SELECT department.chat_id FROM user "
                       "JOIN department ON user.department_id = department.id "
                       "WHERE user.id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='tuple')
    def get_name(user_id, cursor=None):
        cursor.execute("SELECT first_name, last_name FROM user WHERE id=(%s)", (user_id,))

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
    @db.fetch(return_type='all_tuples')
    def clear_skips(cursor=None):
        cursor.execute("UPDATE user SET skips_month=0")
        cursor.execute("SELECT name, chat_id FROM department")

    @staticmethod
    @db.connect
    def set_admin(last_name, make_admin=True, cursor=None):
        last_name = last_name.capitalize()
        cursor.execute("UPDATE user SET is_admin=(%s) WHERE last_name=(%s)", (int(make_admin), last_name))

    @staticmethod
    @db.connect
    def update_next_birthday(user, cursor=None):
        user.birthday = user.birthday.replace(user.birthday.year + 1)
        # cursor.execute("""UPDATE user SET birthday=(%s) where id=(%s)""", (user.birthday, user.id))
