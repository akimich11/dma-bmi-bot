import pickle

from telebot.types import Poll

from base.decorators.db import connector
from polls import utils
from users.models import user_model


class PollModel:
    def __init__(self):
        self.cursor = None
        self.conn = None
        self.polls = dict()
        self.last_poll_id = None
        self.__read_database()

    @connector
    def __read_database(self):
        self.cursor.execute("""SELECT * FROM polls order by creation_date""")
        data = self.cursor.fetchall()
        if data:
            for poll in data:
                self.polls[poll[0]] = pickle.loads(poll[1])
            self.last_poll_id = data[-1][0]

    @connector
    def add_poll(self, poll: Poll):
        self.cursor.execute("""INSERT INTO polls VALUE (%s, %s, %s)""", (poll.id, pickle.dumps((poll, {})), None))
        self.polls[poll.id] = (poll, {})
        self.last_poll_id = poll.id

    @connector
    def update_poll(self, poll: Poll, votes: dict):
        self.cursor.execute("""UPDATE polls SET poll=(%s) WHERE id=(%s)""",
                            (pickle.dumps((poll, votes)), poll.id))

    def get_ignorants_list(self, department=None, poll_question=None):
        ignorants = []
        poll, votes = utils.get_poll(self.polls, self.last_poll_id, poll_question)
        if poll is None:
            return None

        for user in user_model.users.values():
            if user.id not in votes and (
                    department is None or user.department == department.lower()):
                ignorants.append(user)

        return ignorants

    def get_vote_lists(self, poll_question=None):
        students, skippers = [], []
        poll, votes = utils.get_poll(self.polls, self.last_poll_id, poll_question)
        if poll is None:
            return None, None

        for user in user_model.users.values():
            if user.id not in votes:
                probability = utils.get_probability(self.polls, user.id, poll.question)
                students.append((user, probability)) if probability >= 50. else skippers.append((user, probability))
            else:
                for option in votes[user.id]:
                    if 'не' in option.lower():
                        skippers.append((user, 0))
                        break
                else:
                    students.append((user, 100))
        return students, skippers


poll_model = PollModel()
