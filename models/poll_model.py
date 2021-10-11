import pickle

from telebot.types import Poll

from decorators.db import connector
from models.user_model import user_model


class PollModel:
    def __init__(self):
        self.cursor = None
        self.conn = None
        self.polls = dict()
        self.last_poll_id = None
        self.__read_database()

    @connector
    def __read_database(self):
        self.cursor.execute("""SELECT * FROM polls""")
        data = self.cursor.fetchall()
        if data:
            for poll in data:
                self.polls[poll[0]] = pickle.loads(poll[1])
            self.last_poll_id = data[-1][0]

    @connector
    def add_poll(self, poll: Poll):
        self.cursor.execute("""INSERT INTO polls VALUE (%s, %s)""", (poll.id, pickle.dumps((poll, {}))))
        self.polls[poll.id] = (poll, {})
        self.last_poll_id = poll.id

    @connector
    def update_poll(self, poll: Poll, votes: dict):
        self.cursor.execute("""UPDATE polls SET poll=(%s) WHERE id=(%s)""",
                            (pickle.dumps((poll, votes)), poll.id))

    def get_ignorants_list(self, department=None, poll_question=None):
        ignorants = []
        if poll_question is not None:
            for p, v in self.polls.values():
                if poll_question.lower() in p.question.lower():
                    poll, votes = p, v
                    break
            else:
                return None
        else:
            if self.last_poll_id is not None:
                poll, votes = self.polls[self.last_poll_id]
            else:
                return None

        for user in user_model.users.values():
            if user.id not in votes and (
                    department is None or user.department == department.lower()):
                ignorants.append(user)

        return ignorants


poll_model = PollModel()
