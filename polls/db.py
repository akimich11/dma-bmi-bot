from datetime import datetime
from telebot.types import Poll
from base.decorators import db

# todo: проверки на деда


class PollService:
    @staticmethod
    @db.fetch(return_type='value')
    def get_department_id(group_chat_id, cursor=None):
        cursor.execute("SELECT id FROM department WHERE chat_id=(%s)", (group_chat_id,))

    @staticmethod
    @db.connect
    def create_poll(poll: Poll, group_chat_id, cursor=None):
        department_id = PollService.get_department_id(group_chat_id)
        cursor.execute("UPDATE poll SET is_last=0 WHERE is_last=1")
        cursor.execute("INSERT INTO poll VALUE (%s, %s, %s, %s, %s)", (poll.id,
                                                                       department_id,
                                                                       poll.question,
                                                                       datetime.utcnow(),
                                                                       None))
        for option in poll.options:
            cursor.execute("INSERT INTO poll_option VALUE (%s, %s, %s)", (None, poll.id, option.text))

    @staticmethod
    @db.connect
    def update_poll(poll_id, user_id, user_answers, cursor=None):
        if not user_answers:
            cursor.execute("DELETE FROM user_vote WHERE user_id=(%s)", (user_id,))
        for option in user_answers:
            cursor.execute("SELECT id FROM poll_option WHERE poll_id=(%s) AND text=(%s)", (poll_id, option))
            option_id = cursor.fetchone()
            if option_id is not None:
                cursor.execute("INSERT IGNORE INTO user_vote VALUE (%s, %s, %s)", (None, user_id, option_id[0]))

    @staticmethod
    @db.fetch(return_type='value')
    def get_poll_question(poll_id, cursor=None):
        cursor.execute("SELECT question FROM poll where id=(%s)", (poll_id,))

    @staticmethod
    @db.fetch(return_type='all_values')
    def get_poll_options(poll_id, cursor=None):
        cursor.execute("SELECT text FROM poll_option WHERE poll_id=(%s)", (poll_id,))

    @staticmethod
    @db.fetch(return_type='value')
    def get_last_poll_question(user_id, cursor=None):
        cursor.execute("SELECT department_id from user WHERE id=(%s)", (user_id,))
        department_id = cursor.fetchone()[0]
        cursor.execute("SELECT question FROM poll WHERE department_id=(%s) "
                       "ORDER BY creation_date DESC LIMIT 1",
                       (department_id,))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_ignorants_list(group_chat_id, poll_question, cursor=None):
        cursor.execute("""
                        SELECT user.id, first_name, last_name FROM user
                        JOIN poll p on p.department_id = user.department_id
                        JOIN department d on d.id = user.department_id
                        LEFT JOIN user_vote uv ON user.id = uv.user_id
                        WHERE d.chat_id = (%s) AND p.question = (%s) AND uv.user_id IS NULL
                        ORDER BY sub_department DESC, last_name
                        """, (group_chat_id, poll_question))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_votes_for_option(group_chat_id, poll_question, option_text, cursor=None):
        cursor.execute("""
                        SELECT first_name, last_name FROM user
                        JOIN poll p on p.department_id = user.department_id
                        JOIN department d on d.id = user.department_id
                        JOIN user_vote uv ON user.id = uv.user_id
                        JOIN poll_option po on uv.option_id = po.id
                        WHERE d.chat_id = (%s) AND p.question = (%s) AND po.text=(%s)
                        ORDER BY sub_department DESC, last_name
                        """, (group_chat_id, poll_question, option_text))

    @staticmethod
    def get_vote_lists(group_chat_id, poll_question):
        ignorants = PollService.get_ignorants_list(group_chat_id, poll_question)
        students = PollService.get_votes_for_option(group_chat_id, poll_question, option_text='да')
        skippers = PollService.get_votes_for_option(group_chat_id, poll_question, option_text='нет')
        return students or [], skippers or [], ignorants or []
