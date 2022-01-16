from datetime import datetime
from telebot.types import Poll
from base.decorators import db


class PollService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_department_id(group_chat_id, cursor=None):
        cursor.execute("SELECT id FROM departments WHERE chat_id=(%s)", (group_chat_id,))

    @staticmethod
    @db.connect
    def create_poll(poll: Poll, group_chat_id, cursor=None):
        department_id = PollService.get_department_id(group_chat_id)
        cursor.execute("INSERT INTO polls VALUES (%s, %s, %s, %s)", (poll.id,
                                                                     department_id,
                                                                     poll.question,
                                                                     datetime.utcnow()))
        for option in poll.options:
            cursor.execute("INSERT INTO poll_options (poll_id, text) VALUES (%s, %s)", (poll.id, option.text))

    @staticmethod
    @db.connect
    def update_poll(poll_id, user_id, user_answers, cursor=None):
        if not user_answers:
            cursor.execute("DELETE FROM users_poll_options WHERE user_id=(%s)", (user_id,))
        for option in user_answers:
            cursor.execute("SELECT id FROM poll_options WHERE poll_id=(%s) AND text=(%s)", (poll_id, option))
            option_id = cursor.fetchone()
            if option_id is not None:
                cursor.execute("INSERT INTO users_poll_options (user_id, option_id) VALUES (%s, %s)",
                               (user_id, option_id[0]))

    @staticmethod
    @db.fetch(return_type='value')
    def get_poll_question(poll_id, cursor=None):
        cursor.execute("SELECT question FROM polls where id=(%s)", (poll_id,))

    @staticmethod
    @db.fetch(return_type='all_values')
    def get_poll_options(poll_id, cursor=None):
        cursor.execute("SELECT text FROM poll_options WHERE poll_id=(%s)", (poll_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_last_poll_question(user_id, cursor=None):
        cursor.execute("SELECT department_id from users WHERE id=(%s)", (user_id,))
        department_id = cursor.fetchone()[0]
        cursor.execute("SELECT question FROM polls WHERE department_id=(%s) "
                       "ORDER BY created_at DESC LIMIT 1",
                       (department_id,))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_ignorants_list(group_chat_id, poll_question, cursor=None):
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
    def get_votes_for_option(group_chat_id, poll_question, option_text, cursor=None):
        cursor.execute("""
                        SELECT users.id, first_name, last_name
                        FROM users
                            JOIN departments d ON d.id = users.department_id
                            JOIN users_poll_options upo ON users.id = upo.user_id
                            JOIN poll_options po ON upo.option_id = po.id
                            JOIN polls p ON p.id = po.poll_id
                        WHERE d.chat_id = %s AND p.question = %s AND po.text = %s
                        """, (group_chat_id, poll_question, option_text))

    @staticmethod
    def get_vote_lists(group_chat_id, poll_question):
        ignorants = PollService.get_ignorants_list(group_chat_id, poll_question)
        students = PollService.get_votes_for_option(group_chat_id, poll_question, option_text='да')
        skippers = PollService.get_votes_for_option(group_chat_id, poll_question, option_text='нет')
        return students or [], skippers or [], ignorants or []