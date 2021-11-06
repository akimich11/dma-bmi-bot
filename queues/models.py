import pickle
from base.decorators.db import connector
from users.models import user_model

MAX_QUEUE_SIZE = 30


class Queue:
    EMPTY = ''

    def __init__(self, subject, positions=None):
        self.subject = subject
        self.positions = positions or {}

    def __str__(self):
        if self.positions:
            return f'{self.subject}\nОчередь:\n' + \
                   '\n'.join([f'{i}. {user_model.users[user_id].first_name} '
                              f'{user_model.users[user_id].last_name}'
                              for user_id, i in sorted(list(self.positions.items()),
                                                       key=lambda x: x[1])])
        return f'{self.subject}. Очередь пока пустая, занимай пока не поздно'

    def add_to_pos(self, user_id, pos):
        if pos is None:
            pos = 1 if not self.positions else max(self.positions.values()) + 1
            if pos > MAX_QUEUE_SIZE:
                return 'Похоже, кто-то уже занял самое последнее место'
        if pos <= 0 or pos > MAX_QUEUE_SIZE:
            return 'не-не-не'
        if pos not in self.positions.values():
            self.positions[user_id] = pos
            return None
        return 'Это место уже занято'

    def remove(self, user_id):
        self.positions.pop(user_id)


class QueueModel:
    def __init__(self):
        self.cursor = None
        self.conn = None
        self.last_queue = None
        self.queues = dict()
        self.__read_database()

    @connector
    def __read_database(self):
        self.cursor.execute("""SELECT * FROM queues""")
        data = self.cursor.fetchall()
        if data:
            for queue in data:
                self.queues[queue[1]] = Queue(subject=queue[1],
                                              positions=pickle.loads(queue[2]))
                if queue[3] == 1:
                    self.last_queue = queue[1]

    @connector
    def add_queue(self, queue: Queue):
        self.cursor.execute("""INSERT INTO queues VALUE (%s, %s, %s, %s)""", (None,
                                                                          queue.subject,
                                                                          pickle.dumps(queue.positions), 1))
        self.queues[queue.subject] = queue
        self.update_queue(queue)

    @connector
    def update_queue(self, queue: Queue):
        old_last_queue = self.last_queue
        self.last_queue = queue.subject
        self.cursor.execute("""UPDATE queues SET positions=(%s) WHERE subject=(%s)""",
                            (pickle.dumps(queue.positions), queue.subject))
        self.cursor.execute("""UPDATE queues SET is_last=1 WHERE subject=(%s)""", (queue.subject,))
        if old_last_queue is not None and old_last_queue != queue.subject:
            self.cursor.execute("""UPDATE queues SET is_last=0 WHERE subject=(%s)""", (old_last_queue,))

    def sign_up(self, subject, user_id, pos=None):
        if subject is None:
            subject = self.last_queue
        if subject not in queue_model.queues:
            return 'Очередь для заданного предмета не найдена :('
        queue_object = self.queues[subject]
        if user_id in user_model.users and user_id not in queue_object.positions:
            result = queue_object.add_to_pos(user_id, pos)
            if result is None:
                self.update_queue(queue_object)
            return result
        return 'Ты уже есть в очереди'

    def cancel_sign_up(self, subject, user_id):
        if subject is None:
            subject = self.last_queue
        if subject not in queue_model.queues:
            return 'Очередь для заданного предмета не найдена :('
        queue_object = self.queues[subject]
        if user_id in user_model.users and user_id in queue_object.positions:
            queue_object.remove(user_id)
            self.update_queue(queue_object)
            return None
        return 'Тебя и так нет в этой очереди'

    def move(self, subject, user_id, new_pos):
        if subject is None:
            subject = self.last_queue
        if subject not in queue_model.queues:
            return 'Очередь для заданного предмета не найдена :('
        queue_object = self.queues[subject]
        if user_id in user_model.users and user_id in queue_object.positions:
            result = queue_object.add_to_pos(user_id, new_pos)
            if result is None:
                self.update_queue(queue_object)
            return result
        return 'Тебя нет в этой очереди. Используй /sign_up'

    def clear_queue(self, subject):
        if subject is None:
            subject = self.last_queue
        if subject in self.queues:
            self.queues[subject].positions.clear()
            self.update_queue(self.queues[subject])
            return True
        return False
            
    def get_queue(self, subject):
        if subject is None:
            subject = self.last_queue
        if subject in self.queues:
            self.update_queue(self.queues[subject])
            return self.queues[subject]
        return None
       
    def get_all_queues(self):
        return '\n'.join([f'{i + 1}. {name}' for i, name in enumerate(self.queues.keys())])


queue_model = QueueModel()
