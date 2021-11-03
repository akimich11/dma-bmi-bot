import pickle
from base.decorators.db import connector
from users.models import user_model


MAX_QUEUE_SIZE = len(user_model.users) + 20


class Queue:
    EMPTY = ''
    
    def __init__(self, subject, date, queue=None):
        self.subject = subject
        self.date = date
        if queue is None:
            self.queue = [self.EMPTY] * MAX_QUEUE_SIZE
            self.id_to_pos = {}
        else:
            self.queue = queue
            self.id_to_pos = {user_id: i + 1
                              for i, user_id in enumerate(queue)
                              if user_id != self.EMPTY}

    def __str__(self):
        if self.id_to_pos:
            return f'{self.date}, {self.subject}\nОчередь:\n' +\
                   '\n'.join([f'{i + 1}. {user_model.users[user_id].first_name} '
                              f'{user_model.users[user_id].last_name}'
                              for i, user_id in enumerate(self.queue)
                              if user_id != self.EMPTY])
        return f'{self.date}, {self.subject}. Очередь пока пустая, занимай пока не поздно'
        
    def add_to_pos(self, user_id, pos):
        if pos is None:
            pos = 1 if not self.id_to_pos else max(self.id_to_pos.values()) + 1
            if pos > MAX_QUEUE_SIZE:
                return 'Похоже, кто-то уже занял самое последнее место.'
        if pos <= 0 or pos > MAX_QUEUE_SIZE:
            return 'не-не-не'
        if self.queue[pos - 1] == self.EMPTY:
            self.queue[pos - 1] = user_id
            self.id_to_pos[user_id] = pos
            return None
        else:
            return 'Это место уже занято.'
            
    def remove(self, user_id):
        self.queue[self.id_to_pos[user_id] - 1] = self.EMPTY
        self.id_to_pos.pop(user_id)
    


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

    def sign_up(self, date, subject, user_id, pos=None):
        if (date, subject) not in queue_model.queues:
            return 'Очередь для заданных предмета и даты не найдена :('
        queue_object = self.queues[(date, subject)]
        if user_id in user_model.users and user_id not in queue_object.queue:
            ret = queue_object.add_to_pos(user_id, pos)
            if ret is None:
                self.update_queue(queue_object)
            return ret
        return 'Ты уже есть в очереди.'
        
    def cancel_sign_up(self, date, subject, user_id):
        if (date, subject) not in queue_model.queues:
            return 'Очередь для заданных предмета и даты не найдена :('
        queue_object = self.queues[(date, subject)]
        if user_id in user_model.users and user_id in queue_object.id_to_pos:
            queue_object.remove(user_id)
            self.update_queue(queue_object)
            return None
        return 'Тебя и так нет в этой очереди.'
        
    def move(self, date, subject, user_id, new_pos):
        if (date, subject) not in queue_model.queues:
            return 'Очередь для заданных предмета и даты не найдена :('
        queue_object = self.queues[(date, subject)]
        if user_id in user_model.users and user_id in queue_object.id_to_pos:
            old_pos = queue_object.id_to_pos.user_id
            ret = queue_object.add_to_pos(user_id, pos)
            if ret is None:
                queue_object.queue[old_pos - 1] = queue_object.EMPTY
                self.update_queue(queue_object)
            return ret
        return 'Тебя нет в этой очереди. Используй /sign_up.'

    def clear_queue(self, date, subject):
        if (date, subject) in self.queues:
            self.queues[(date, subject)].queue = []
            self.update_queue(self.queues[(date, subject)])
            return True
        return False


queue_model = QueueModel()
