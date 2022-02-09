from base import db


class UserService(db.ConnectionMixin):
    @classmethod
    @db.fetch(return_type='value')
    def get_department_id(cls, chat_id, user_id, cursor):
        if chat_id == user_id:
            cursor.execute("SELECT department_id FROM users WHERE id=%s", (user_id,))
        else:
            cursor.execute("SELECT id FROM departments WHERE chat_id=%s", (chat_id,))

    @classmethod
    @db.fetch(return_type='value')
    def get_group_chat_id(cls, user_id, cursor):
        cursor.execute("SELECT departments.chat_id FROM users "
                       "JOIN departments ON users.department_id = departments.id "
                       "WHERE users.id=(%s)", (user_id,))

    @classmethod
    @db.fetch(return_type='tuple')
    def get_name(cls, user_id, cursor):
        cursor.execute("SELECT first_name, last_name FROM users WHERE id=(%s)", (user_id,))

    @classmethod
    @db.fetch(return_type='value')
    def get_is_admin(cls, user_id, cursor):
        cursor.execute("SELECT is_admin FROM users WHERE id=(%s)", (user_id,))

    @classmethod
    @db.get_cursor
    def set_admin(cls, last_name, make_admin=True, cursor=None):
        last_name = last_name.capitalize()
        cursor.execute("UPDATE users SET is_admin=(%s) WHERE last_name=(%s)", (int(make_admin), last_name))

    @classmethod
    @db.fetch(return_type='tuple')
    def get_departments(cls, user_id, cursor=None):
        cursor.execute("SELECT department_id, sub_department FROM users WHERE id=%s", (user_id,))

    @classmethod
    @db.fetch(return_type='all_tuples')
    def get_group_list(cls, user_id, order_by_department, cursor):
        if order_by_department:
            cursor.execute("SELECT last_name, first_name FROM users "
                           "WHERE department_id=(SELECT department_id from users WHERE id=%s) "
                           "ORDER BY sub_department DESC, last_name", (user_id,))
        else:
            cursor.execute("SELECT last_name, first_name FROM users "
                           "WHERE department_id=(SELECT department_id from users WHERE id=%s) "
                           "ORDER BY last_name", (user_id,))

    @classmethod
    @db.fetch(return_type='value')
    def get_user_count(cls, department_id, cursor):
        cursor.execute("SELECT COUNT(*) FROM users WHERE department_id=(%s)", (department_id,))

    @classmethod
    @db.fetch(return_type='value')
    def get_sub_department(cls, user_id, cursor):
        cursor.execute("SELECT sub_department FROM users WHERE id=%s", (user_id,))
