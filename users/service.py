from base.decorators import db


class UserService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_group_chat_id(user_id, cursor):
        cursor.execute("SELECT departments.chat_id FROM users "
                       "JOIN departments ON users.department_id = departments.id "
                       "WHERE users.id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='tuple')
    def get_name(user_id, cursor):
        cursor.execute("SELECT first_name, last_name FROM users WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_is_admin(user_id, cursor):
        cursor.execute("SELECT is_admin FROM users WHERE id=(%s)", (user_id,))

    @staticmethod
    @db.connect
    def set_admin(last_name, make_admin=True, cursor=None):
        last_name = last_name.capitalize()
        cursor.execute("UPDATE users SET is_admin=(%s) WHERE last_name=(%s)", (int(make_admin), last_name))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_group_list(user_id, order_by_department, cursor):
        if order_by_department:
            cursor.execute("SELECT last_name, first_name FROM users "
                           "WHERE department_id=(SELECT department_id from users WHERE id=%s) "
                           "ORDER BY sub_department DESC, last_name", (user_id,))
        else:
            cursor.execute("SELECT last_name, first_name FROM users "
                           "WHERE department_id=(SELECT department_id from users WHERE id=%s) "
                           "ORDER BY last_name", (user_id,))
