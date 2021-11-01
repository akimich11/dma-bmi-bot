import pickle
from base.decorators.db import connector
from users.models import user_model


class Queue:
    def __init__(self, subject, date, queue=None):
        self.subject = subject
        self.date = date
        self.queue = queue or []

    def __str__(self):
        if self.queue:
            return f'Дата: {self.date}, предмет: {self.subject}. Очередь:\n' +\
                   '\n'.join([f'{user_model.users[user_id].first_name} '
                              f'{user_model.users[user_id].last_name}' for user_id in self.queue])
        return f'Дата: {self.date}, предмет: {self.subject}. Очередь пока пустая, давай занимай пока не поздно'


class QueueModel:
    def __init__(self):
        self.cursor = None
        self.conn = None
        self.queues = dict()
        self.__read_database()

    @connector
    def __read_database(self):
        self.cursor.execute("""SELECT * FROM queues""")
        data = self.cursor.fetchall()
        if data:
            for queue in data:
                self.queues[(queue[2], queue[1])] = Queue(*queue[1:3], pickle.loads(queue[3]))

    @connector
    def add_queue(self, queue: Queue):
        self.cursor.execute("""INSERT INTO queues VALUE (%s, %s, %s, %s)""", (None,
                                                                              queue.subject,
                                                                              queue.date,
                                                                              pickle.dumps(queue.queue)))
        self.queues[(queue.date, queue.subject)] = queue

    @connector
    def update_queue(self, queue: Queue):
        self.cursor.execute("""UPDATE queues SET queue=(%s) WHERE subject=(%s) and date=(%s)""",
                            (pickle.dumps(queue.queue), queue.subject, queue.date))

    def sign_up(self, date, subject, user_id):
        if (date, subject) not in queue_model.queues:
            return False
        queue_object = self.queues[(date, subject)]
        if user_id in user_model.users and user_id not in queue_object.queue:
            queue_object.queue.append(user_id)
            self.update_queue(queue_object)
            return True
        return False

    def clear_queue(self, date, subject):
        if (date, subject) in self.queues:
            self.queues[(date, subject)].queue = []
            self.update_queue(self.queues[(date, subject)])
            return True
        return False


queue_model = QueueModel()
