import datetime

from base.decorators.db import connector


class User:
    def __init__(self, **kwargs):
        self.username = None if kwargs['username'] == 'undefined' else kwargs['username']
        self.first_name = kwargs['first_name']
        self.last_name = kwargs['last_name']
        self.id = int(kwargs['id'])
        self.is_admin = bool(kwargs['is_admin'])
        self.department = kwargs['department'].lower()
        self.skips_month = kwargs['skips_month']
        self.skips_semester = kwargs['skips_semester']
        self.birthday = kwargs['birthday']


class UserModel:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.users = dict()
        self.last_names = dict()
        self.__read_database()

    @connector
    def __read_database(self):
        self.cursor.execute("""SELECT * FROM users ORDER BY department, last_name""")
        data = self.cursor.fetchall()
        column_names = [column[0] for column in self.cursor.description]
        if data is not None:
            for row in data:
                kwargs = dict(zip(column_names, row))
                self.users[kwargs['id']] = User(**kwargs)
            for user in self.users.values():
                self.last_names[user.last_name] = user

    def get_skips(self, user_id):
        if user_id not in self.users:
            return 'чел тебя нет в списке', 'чел тебя нет в списке'
        return self.users[user_id].skips_month, self.users[user_id].skips_semester

    @connector
    def __set_skips(self, user, skips_month, skips_semester):
        self.cursor.execute("UPDATE users SET skips_month=(%s), "
                            "skips_semester=(%s) WHERE id=(%s)", (skips_month, skips_semester, user.id))

    def set_skips(self, last_name, skips_month, skips_semester):
        if last_name in self.last_names:
            self.__set_skips(self.last_names[last_name], skips_month, skips_semester)

    def inc_skips(self, last_names):
        for last_name in last_names:
            user = self.last_names[last_name]
            self.__set_skips(user, user.skips_month + 2, user.skips_semester + 2)
            user.skips_month += 2
            user.skips_semester += 2

    def clear_skips(self):
        for user in self.users.values():
            self.__set_skips(user, 0, user.skips_semester)
            user.skips_month = 0

    @connector
    def set_admin(self, last_name, make_admin=True):
        last_name = last_name.capitalize()
        self.cursor.execute("UPDATE users SET is_admin=(%s) WHERE last_name=(%s)", (int(make_admin), last_name))
        if last_name in self.last_names:
            self.last_names[last_name].is_admin = make_admin
            return True
        return False

    @connector
    def update_next_birthday(self, user):
        user.birthday = user.birthday.replace(user.birthday.year + 1)
        self.cursor.execute("""UPDATE users SET birthday=(%s) where id=(%s)""", (user.birthday, user.id))


user_model = UserModel()
