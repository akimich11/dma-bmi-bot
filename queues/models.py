import pickle
from base.decorators.db import connector
from queues import status
from users.models import user_model

MAX_QUEUE_SIZE = 30


class Queue:
    def __init__(self, name, positions=None):
        self.name = name
        self.positions = positions or {}

    def __str__(self):
        if self.positions:
            sorted_queue = sorted(list(self.positions.items()),
                                  key=lambda x: x[1])
            return f'{self.name}\nОчередь:\n' + \
                   '\n'.join([f'{i}. {user_model.users[user_id].first_name} '
                              f'{user_model.users[user_id].last_name}'
                              for user_id, i in sorted_queue])
        return f'{self.name}. Очередь пока пустая, занимай пока не поздно'

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
        self.last_queue_name = None
        self.queues = dict()
        self._read_database()

    @connector
    def _read_database(self):
        self.cursor.execute("""SELECT * FROM queues""")
        data = self.cursor.fetchall()
        if data:
            for _, name, queue_str, is_last in data:
                self.queues[name] = Queue(name=name,
                                          positions=pickle.loads(queue_str))
                if is_last == 1:
                    self.last_queue_name = name
                    
    @connector
    def _update_last_queue(self, name):
        if self.last_queue_name == name:
            return
        old_last_queue = self.last_queue_name
        self.last_queue_name = name
        self.cursor.execute("""UPDATE queues SET is_last=1 WHERE subject=(%s)""",
                            (name,))
        if old_last_queue is not None:
            self.cursor.execute("""UPDATE queues SET is_last=0 WHERE subject=(%s)""",
                                (old_last_queue,))

    @connector
    def add_queue(self, queue: Queue):
        if queue.name in self.queues:
    	    status.handler.error('Очередь с таким именем уже существует')
    	    return
        self.cursor.execute("""INSERT INTO queues VALUE (%s, %s, %s, %s)""",
                            (None, queue.name, pickle.dumps(queue.positions), 1))
        self.queues[queue.name] = queue
        self._update_last_queue(queue.name)
        
    @connector
    def remove_queue(self, name):
        queue = self._get_queue(name)
        if queue is None:
            return None
        self.queues.pop(name)
        self.cursor.execute("""DELETE FROM queues WHERE subject=(%s)""", (name,))
        if self.last_queue_name == name:
            self.last_queue_name = None

    @connector
    def _update_queue(self, queue: Queue):
        self.cursor.execute("""UPDATE queues SET positions=(%s) WHERE subject=(%s)""",
                            (pickle.dumps(queue.positions), queue.name))
        self._update_last_queue(queue.name)

    def sign_up(self, name, user_id, pos):
        queue = self._get_queue(name)
        if queue is None:
            return None, None
        elif user_id in queue.positions:
            status.handler.error('Ты уже есть в очереди')
        elif user_id in user_model.users:
            result = queue.add_to_pos(user_id, pos)
            if result is None:
                self._update_queue(queue)
                return queue.name, queue.positions[user_id]
        return None, None

    def cancel_sign_up(self, name, user_id):
        queue = self._get_queue(name)
        if queue is None:
            return None
        elif user_id not in queue.positions:
            status.handler.error('Тебя и так нет в этой очереди')
        elif user_id in user_model.users:
            queue.remove(user_id)
            self._update_queue(queue)
            return queue.name
            
        return None

    def move(self, name, user_id, pos):
        queue = self._get_queue(name)
        if queue is None:
            return None, None
        elif user_id not in queue.positions:
            status.handler.error('Тебя нет в этой очереди. Используй /sign_up')
        elif user_id in user_model.users:
            result = queue.add_to_pos(user_id, pos)
            if result is None:
                self._update_queue(queue)
                return queue.name, queue.positions[user_id]
        return None, None

    def clear_queue(self, name):
        queue = self._get_queue(name)
        if queue is not None:
            queue.positions.clear()
            self._update_queue(queue)
            
    def get_queue(self, name):
        queue = self._get_queue(name)
        self._update_last_queue(queue.name)
        return str(queue)
       
    def get_all_queues(self):
        return '\n'.join([f'{i + 1}. {name}' for i, name in enumerate(self.queues.keys())])
        
    def _get_queue(self, name):
        if name is None:
            name = self.last_queue_name
        if name in self.queues:
            return self.queues[name]
        else:
            status.handler.error('Очередь для заданного предмета не найдена :(')


queue_model = QueueModel()
