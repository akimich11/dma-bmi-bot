from base.decorators import db
from queues.errors import QueueException

class QueueService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_department_id(group_chat_id, cursor=None):
        cursor.execute("SELECT id FROM departments WHERE chat_id=(%s)", (group_chat_id,))
        
    @staticmethod
    @db.fetch(return_type='value')
    def get_queue_id(queue_name, department_id, cursor=None):
        cursor.execute("SELECT id FROM queues WHERE name=(%s) AND department_id=(%s)",
                       (queue_name, department_id))
                       
    @staticmethod
    @db.connect
    def get_queue_id_or_last(queue_name, department_id, cursor=None):
        if queue_name is None:
            queue_id = QueueService.get_last_queue(department_id)
            if queue_id is not None:
                cursor.execute("SELECT name FROM queues WHERE id=(%s)", (queue_id,))
                queue_name = cursor.fetchone()[0]
        else:
            queue_id = QueueService.get_queue_id(queue_name, department_id)
        
        if queue_id is None:
            raise QueueException('Очередь не найдена')
            
        return queue_id, queue_name
                                          
                       
    @staticmethod
    @db.fetch(return_type='value')
    def get_max_pos(queue_id, cursor=None):
        cursor.execute("SELECT MAX(position) FROM queue_positions WHERE queue_id=(%s)",
                       (queue_id,))
                       
    @staticmethod
    @db.connect
    def check_pos(queue_id, pos, cursor=None):
        if pos is None:
            pos = QueueService.get_max_pos(queue_id)
            pos = 1 if pos is None else pos + 1
        if pos <= 0 or pos > 32:
            raise QueueException('не-не-не')

        cursor.execute("SELECT * FROM queue_positions WHERE position=(%s) AND queue_id=(%s)",
                       (pos, queue_id))
        if cursor.fetchone() is not None:
            raise QueueException('занято')
        return pos  
        
    @staticmethod
    @db.connect
    def set_last_queue(new_last_id, department_id, cursor=None):
        cursor.execute("UPDATE queues SET is_last=0 WHERE department_id=(%s)", (department_id,))
        cursor.execute("UPDATE queues SET is_last=1 WHERE id=(%s)", (new_last_id,))
        
    @staticmethod
    @db.fetch(return_type='value')
    def get_last_queue(department_id, cursor=None):
        cursor.execute("SELECT id FROM queues WHERE department_id=(%s) AND is_last=1",
                       (department_id,))

    @staticmethod
    @db.connect
    def create_queue(group_chat_id, queue_name, cursor=None):
        department_id = QueueService.get_department_id(group_chat_id)
        if QueueService.get_queue_id(queue_name, department_id) is not None:
            raise QueueException('Очередь с таким именем уже существует')
        cursor.execute("INSERT INTO queues VALUES (%s, %s, %s)",
                       (1, queue_name, department_id))
        QueueService.set_last_queue(
            QueueService.get_queue_id(queue_name, department_id), department_id)
            
    @staticmethod
    @db.connect
    def remove_queue(group_chat_id, queue_name, cursor=None):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, _ = QueueService.get_queue_id_or_last(queue_name, department_id)
        cursor.execute("DELETE FROM queues WHERE id=(%s)", (queue_id,))
        
    @staticmethod
    @db.connect
    def sign_up(group_chat_id, queue_name, user_id, pos, cursor=None):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        pos = QueueService.check_pos(queue_id, pos)
        
        cursor.execute("SELECT * FROM queue_positions WHERE user_id=(%s) AND queue_id=(%s)",
                       (user_id, queue_id))
        if cursor.fetchone() is not None:
            raise QueueException('Ты уже есть в очереди')
            
        cursor.execute("INSERT INTO queue_positions VALUES (%s, %s, %s)",
                       (pos, queue_id, user_id))
        QueueService.set_last_queue(queue_id, department_id)
        return queue_name, pos

