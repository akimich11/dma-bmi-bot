import pickle

from telebot.types import Poll

from base.decorators.db import connector
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

    def __get_poll(self, poll_question):
        if poll_question is not None:
            for p, v in self.polls.values():
                if poll_question.lower() in p.question.lower():
                    return p, v
            else:
                return None, None
        else:
            if self.last_poll_id is not None:
                return self.polls[self.last_poll_id]
            return None, None

    def get_ignorants_list(self, department=None, poll_question=None):
        ignorants = []
        poll, votes = self.__get_poll(poll_question)
        if poll is None:
            return None

        for user in user_model.users.values():
            if user.id not in votes and (
                    department is None or user.department == department.lower()):
                ignorants.append(user)

        return ignorants

    def __get_stats(self, user_id, poll_question):
        num_attends = 0
        num_polls = 0
        for p, v in self.polls.values():
            if poll_question.lower() in p.question.lower() and user_id in v and 'да' in v[user_id]:
                num_attends += 1
            num_polls += 1
        return 100. * (num_attends / num_polls)

    def get_vote_list(self, poll_question=None):
        students, skippers = [], []
        poll, votes = self.__get_poll(poll_question)
        if poll is None:
            return None, None

        for user in user_model.users.values():
            if user.id not in votes:
                probability = self.__get_stats(user.id, poll.question)
                students.append((user, probability)) if probability >= 50. else skippers.append((user, probability))
            elif 'да' in votes[user.id]:
                students.append((user, 100))
            else:
                skippers.append((user, 0))
        return students, skippers


poll_model = PollModel()
