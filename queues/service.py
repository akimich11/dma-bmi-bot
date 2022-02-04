from base.decorators import db
from queues.errors import QueueException
from users.service import UserService

class QueueService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_department_id(group_chat_id, cursor):
        cursor.execute("SELECT id FROM departments WHERE chat_id=(%s)", (group_chat_id,))
        
    @staticmethod
    @db.fetch(return_type='value')
    def get_queue_id(queue_name, department_id, cursor):
        cursor.execute("SELECT id FROM queues WHERE name=(%s) AND department_id=(%s)",
                       (queue_name, department_id))
                       
    @staticmethod
    @db.connect
    def check_user_in_queue(queue_id, user_id, is_expected, cursor):
        cursor.execute("SELECT * FROM queue_positions WHERE user_id=(%s) AND queue_id=(%s)",
                       (user_id, queue_id))
        if is_expected and cursor.fetchone() is None:
            raise QueueException('Тебя нет в очереди')
        if not is_expected and cursor.fetchone() is not None:
            raise QueueException('Ты уже есть в очереди')
                       
    @staticmethod
    @db.connect
    def get_queue_id_or_last(queue_name, department_id, cursor):
        if queue_name is None:
            cursor.execute("SELECT id FROM queues WHERE department_id=(%s) AND is_last=1",
                           (department_id,))
            queue_id = cursor.fetchone()
            if queue_id is not None:
                queue_id = queue_id[0]
                cursor.execute("SELECT name FROM queues WHERE id=(%s)", (queue_id,))
                queue_name = cursor.fetchone()[0]
        else:
            queue_id = QueueService.get_queue_id(queue_name, department_id)
        
        if queue_id is None:
            raise QueueException('Очередь не найдена')
            
        return queue_id, queue_name
                       
    @staticmethod
    @db.connect
    def check_pos(department_id, queue_id, pos, cursor):
        if pos is None:
            cursor.execute("SELECT position FROM queue_positions WHERE queue_id=(%s) ORDER BY position",
                           (queue_id,))
            positions = cursor.fetchall()
            positions = [pos_tuple[0] for pos_tuple in positions]
            for i, i_pos in enumerate(positions):
                if i + 1 != i_pos:
                    pos = i + 1
                    break
            if pos is None:
                pos = positions[-1] + 1
        if pos <= 0 or pos > UserService.get_user_count(department_id) + 1:
            raise QueueException('не-не-не')

        cursor.execute("SELECT * FROM queue_positions WHERE position=(%s) AND queue_id=(%s)",
                       (pos, queue_id))
        if cursor.fetchone() is not None:
            raise QueueException('занято')
        return pos  
        
    @staticmethod
    @db.connect
    def set_last_queue(new_last_id, department_id, cursor):
        cursor.execute("UPDATE queues SET is_last=0 WHERE department_id=(%s)", (department_id,))
        cursor.execute("UPDATE queues SET is_last=1 WHERE id=(%s)", (new_last_id,))
                       
    @staticmethod
    @db.connect
    def shift_queue(queue_id, first_pos, cursor):
        cursor.execute("UPDATE queue_positions SET position=position-1 "
                       "WHERE queue_id=(%s) AND position>=(%s)",
                       (queue_id, first_pos))

    @staticmethod
    @db.connect
    def create_queue(group_chat_id, queue_name, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        if QueueService.get_queue_id(queue_name, department_id) is not None:
            raise QueueException('Очередь с таким именем уже существует')
        cursor.execute("INSERT INTO queues VALUES (%s, %s, %s) RETURNING id",
                       (1, queue_name, department_id))
        QueueService.set_last_queue(cursor.fetchone()[0], department_id)
            
    @staticmethod
    @db.connect
    def remove_queue(group_chat_id, queue_name, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, _ = QueueService.get_queue_id_or_last(queue_name, department_id)
        cursor.execute("DELETE FROM queues WHERE id=(%s)", (queue_id,))
        
    @staticmethod
    @db.connect
    def sign_up(group_chat_id, queue_name, user_id, pos, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        pos = QueueService.check_pos(department_id, queue_id, pos)
        QueueService.check_user_in_queue(queue_id, user_id, False)
            
        cursor.execute("INSERT INTO queue_positions VALUES (%s, %s, %s)",
                       (pos, queue_id, user_id))
        QueueService.set_last_queue(queue_id, department_id)
        return queue_name, pos
        
    @staticmethod
    @db.connect
    def move(group_chat_id, queue_name, user_id, pos, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        pos = QueueService.check_pos(department_id, queue_id, pos)
        QueueService.check_user_in_queue(queue_id, user_id, True)
            
        cursor.execute("UPDATE queue_positions SET position=(%s) "
                       "WHERE user_id=(%s) AND queue_id=(%s)",
                       (pos, user_id, queue_id))
        QueueService.set_last_queue(queue_id, department_id)
        return queue_name, pos
        
    @staticmethod
    @db.connect
    def cancel_sign_up(group_chat_id, queue_name, user_id, is_shift, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        QueueService.check_user_in_queue(queue_id, user_id, True)
        
        cursor.execute("DELETE FROM queue_positions WHERE user_id=(%s) AND queue_id=(%s) "
                       "RETURNING position",
                       (user_id, queue_id))
        pos = cursor.fetchone()[0]
        if is_shift:
            QueueService.shift_queue(queue_id, pos + 1)
        QueueService.set_last_queue(queue_id, department_id)
        return queue_name
        
    @staticmethod
    @db.connect
    def shift_first(group_chat_id, queue_name, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        
        
        cursor.execute("DELETE FROM queue_positions WHERE queue_id=(%s) AND "
                       "position=(SELECT MIN(position) FROM queue_positions WHERE queue_id=(%s)) "
                       "RETURNING user_id",
                       (queue_id, queue_id))
        user_id = cursor.fetchone()
        if user_id is None:
            raise QueueException('Очередь и так пустая')
            
        QueueService.shift_queue(queue_id, 1)
        QueueService.set_last_queue(queue_id, department_id)
        return queue_name, user_id[0]
        
    @staticmethod
    @db.connect
    def get_queue_data(group_chat_id, queue_name, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        
        cursor.execute("SELECT position, user_id FROM queue_positions WHERE queue_id=(%s)",
                       (queue_id,))
        data = cursor.fetchall()
        QueueService.set_last_queue(queue_id, department_id)
        return queue_name, data
        
    @staticmethod
    @db.fetch(return_type='all_values')
    def get_all_queues(group_chat_id, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        cursor.execute("SELECT name FROM queues WHERE department_id=(%s) ORDER BY id",
                       (department_id,))
        
    @staticmethod
    @db.connect
    def clear_queue(group_chat_id, queue_name, cursor):
        department_id = QueueService.get_department_id(group_chat_id)
        queue_id, queue_name = QueueService.get_queue_id_or_last(queue_name, department_id)
        cursor.execute("DELETE FROM queue_positions WHERE queue_id=(%s)", (queue_id,))
        QueueService.set_last_queue(queue_id, department_id)
    
