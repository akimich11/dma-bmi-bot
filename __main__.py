import os
import pickle
from telebot import TeleBot, types
import functools
import config


class User:
    def __init__(self, user_id, username, last_name, first_name, department, is_admin):
        self.username = None if username == 'undefined' else username
        self.first_name = first_name
        self.last_name = last_name
        self.id = int(user_id)
        self.department = department
        self.is_admin = is_admin == 'True'
        self.has_voted = False


class PollBot(TeleBot):
    def __init__(self, token):
        super().__init__(token)
        if os.path.isfile('poll.pickle'):
            with open('poll.pickle', 'rb') as f:
                self.poll = pickle.load(f)
        else:
            self.poll = None
        with open('users.csv') as f:
            self.users = {user.id: user for user in [User(*line.strip('\n').split(',')) for line in f.readlines()]}
        self.cursor = None
        self.conn = None

    def send_poll(self, *args, **kwargs) -> types.Message:
        for user in bot.users.values():
            user.has_voted = False
        result = super(PollBot, self).send_poll(*args, **kwargs)
        self.__clear_poll()
        self.poll = result.poll
        with open('poll.pickle', 'wb') as f:
            pickle.dump(self.poll, f)
        return result

    def handle_poll_answer(self, poll_answer):
        if self.poll is not None and self.poll.id == poll_answer.poll_id:
            all_answers = [option.text for option in self.poll.options]
            user_answers = [all_answers[i] for i in poll_answer.option_ids]
            self.users[poll_answer.user.id].has_voted = True
            if len(user_answers):
                self.send_message(config.AKIM_ID,
                                 f'{poll_answer.user.first_name}{f" {poll_answer.user.last_name}" or ""} '
                                 f'voted for {user_answers} in "{self.poll.question}" poll')
            else:
                self.users[poll_answer.user.id].has_voted = False
                self.send_message(config.AKIM_ID, f'{poll_answer.user.first_name} retracted vote '
                                                 f'in "{self.poll.question}" poll')

    def __clear_poll(self):
        self.poll = None
        with open('poll.pickle', 'wb') as f:
            pickle.dump(self.poll, f)


bot = PollBot(token=config.TOKEN)
bot.register_poll_answer_handler(bot.handle_poll_answer, None)


def admin_only(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        if bot.users[message.from_user.id].is_admin:
            return func(message, *args, **kwargs)
        else:
            bot.send_message(message.chat.id, 'Команда доступна только старостам')
    return wrapped


@bot.message_handler(commands=['stats'])
@admin_only
def send_stats(message):
    bot.send_message(message.chat.id, f'Не проголосовали:\n' +
                     '\n'.join([f"[{user.first_name} {user.last_name}](tg://user?id={user.id})"
                                for user in bot.users.values() if not user.has_voted]), parse_mode='Markdown')


@bot.message_handler(content_types=['poll'])
@admin_only
def reply(message):
    poll = message.poll
    bot.send_poll(chat_id=config.AKIM_ID,
                  question=poll.question,
                  options=[option.text for option in poll.options],
                  is_anonymous=poll.is_anonymous,
                  allows_multiple_answers=poll.allows_multiple_answers
                  )


if __name__ == '__main__':
    bot.send_message(config.AKIM_ID, 'started')


bot.polling(none_stop=True)
