from base.user import User
from base.decorators import connector


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
        if data is not None:
            for row in data:
                self.users[row[0]] = User(*row)
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
    def make_admin(self, last_name):
        self.cursor.execute("UPDATE users SET is_admin=1 WHERE last_name=(%s)", (last_name, ))
        self.last_names[last_name].is_admin = True
        return True

    @connector
    def remove_admin(self, last_name):
        self.cursor.execute("UPDATE users SET is_admin=0 WHERE last_name=(%s)", (last_name, ))
        self.last_names[last_name].is_admin = True
        return True


user_model = UserModel()
