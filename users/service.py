from base.decorators import db

# todo: проверки на деда


class UserService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_group_chat_id(user_id, cursor=None):
        cursor.execute("SELECT departments.chat_id FROM users "
                       "JOIN departments ON users.department_id = departments.id "
                       "WHERE users.id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='tuple')
    def get_name(user_id, cursor=None):
        cursor.execute("SELECT first_name, last_name FROM users WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_is_admin(user_id, cursor=None):
        cursor.execute("SELECT is_admin FROM users WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.connect
    def set_admin(last_name, make_admin=True, cursor=None):
        last_name = last_name.capitalize()
        cursor.execute("UPDATE users SET is_admin=(%s) WHERE last_name=(%s)", (int(make_admin), last_name))

    @staticmethod
    @db.fetch(return_type='tuple')
    def get_departments(user_id, cursor=None):
        cursor.execute("SELECT department_id, sub_department FROM users WHERE id=%s", (user_id,))
