from base.decorators import db

# todo: проверки на деда


class UserService:
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
    @db.fetch(return_type='value')
    def get_is_admin(user_id, cursor=None):
        cursor.execute("SELECT is_admin FROM user WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.connect
    def set_admin(last_name, make_admin=True, cursor=None):
        last_name = last_name.capitalize()
        cursor.execute("UPDATE user SET is_admin=(%s) WHERE last_name=(%s)", (int(make_admin), last_name))
