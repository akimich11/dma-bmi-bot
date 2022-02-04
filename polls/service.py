from datetime import datetime
from telebot.types import Poll
from base.decorators import db
from base.exceptions import ObjectNotFound


class PollService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_department_id(group_chat_id,  cursor):
        cursor.execute("SELECT id FROM departments WHERE chat_id=(%s)", (group_chat_id,))

    @staticmethod
    @db.connect
    def create_poll(poll: Poll, group_chat_id,  cursor):
        department_id = PollService.get_department_id(group_chat_id)
        cursor.execute("INSERT INTO polls VALUES (%s, %s, %s, %s)", (poll.id,
                                                                     department_id,
                                                                     poll.question,
                                                                     datetime.utcnow()))
        for option in poll.options:
            cursor.execute("INSERT INTO poll_options (poll_id, text) VALUES (%s, %s)", (poll.id, option.text))

    @staticmethod
    @db.connect
    def update_poll(poll_id, user_id, user_answers,  cursor):
        if not user_answers:
            cursor.execute("DELETE FROM users_poll_options upo USING poll_options po, polls p "
                           "WHERE user_id=(%s) AND upo.option_id=po.id AND po.poll_id=p.id AND p.id=%s",
                           (user_id, poll_id))
        for option in user_answers:
            cursor.execute("SELECT id FROM poll_options WHERE poll_id=(%s) AND text=(%s)", (poll_id, option))
            option_id = cursor.fetchone()
            if option_id is not None:
                cursor.execute("INSERT INTO users_poll_options (user_id, option_id) VALUES (%s, %s)",
                               (user_id, option_id[0]))

    @staticmethod
    @db.fetch(return_type='value')
    def get_poll_question(poll_id,  cursor):
        cursor.execute("SELECT question FROM polls where id=(%s)", (poll_id,))

    @staticmethod
    @db.fetch(return_type='all_values')
    def get_options_by_poll_id(poll_id, cursor):
        cursor.execute("SELECT text FROM poll_options WHERE poll_id=(%s)", (poll_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_last_poll_question(user_id,  cursor):
        cursor.execute("SELECT department_id from users WHERE id=(%s)", (user_id,))
        department_id = cursor.fetchone()
        cursor.execute("SELECT question FROM polls WHERE department_id=(%s) "
                       "ORDER BY created_at DESC LIMIT 1",
                       department_id)

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_ignorants_list(group_chat_id, poll_question, cursor):
        cursor.execute("SELECT id FROM polls WHERE question=%s", (poll_question,))
        if cursor.fetchone() is None:
            raise ObjectNotFound('Опрос не найден')
        cursor.execute("""
                        WITH voters AS (
                          SELECT users.id, first_name, last_name
                          FROM users
                            JOIN departments d ON d.id = users.department_id
                            JOIN users_poll_options upo ON users.id = upo.user_id
                            JOIN poll_options po ON upo.option_id = po.id
                            JOIN polls p ON p.id = po.poll_id
                          WHERE d.chat_id = %s AND p.question = %s
                        )
                        SELECT users.id, first_name, last_name
                        FROM users
                            JOIN departments d ON d.id = users.department_id
                            LEFT JOIN voters USING (last_name, first_name)
                        WHERE voters.id IS NULL AND d.chat_id = %s
                        ORDER BY last_name
                        """, (group_chat_id, poll_question, group_chat_id))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_votes_for_option(group_chat_id, poll_question, option_text,  cursor):
        cursor.execute("""
                        SELECT first_name, last_name
                        FROM users
                            JOIN departments d ON d.id = users.department_id
                            JOIN users_poll_options upo ON users.id = upo.user_id
                            JOIN poll_options po ON upo.option_id = po.id
                            JOIN polls p ON p.id = po.poll_id
                        WHERE d.chat_id = %s AND p.question = %s AND po.text = %s
                        ORDER BY last_name
                        """, (group_chat_id, poll_question, option_text))

    @staticmethod
    @db.fetch(return_type='all_values')
    def get_options_by_poll_question(group_chat_id, poll_question, cursor):
        cursor.execute("SELECT id FROM polls WHERE question=%s", (poll_question,))
        if cursor.fetchone() is None:
            raise ObjectNotFound('Опрос не найден')
        cursor.execute("SELECT text FROM poll_options "
                       "JOIN polls p on poll_options.poll_id = p.id "
                       "JOIN departments d ON p.department_id = d.id "
                       "WHERE d.chat_id=%s AND p.question=%s", (group_chat_id, poll_question))

    @staticmethod
    def get_vote_lists(group_chat_id, poll_question):
        options = PollService.get_options_by_poll_question(group_chat_id, poll_question)
        votes = [PollService.get_votes_for_option(group_chat_id, poll_question, option) for option in options]
        return options, votes
