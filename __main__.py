import os
import pickle
import config
from telebot import TeleBot, types
from decorators import admin_only


class PollBot(TeleBot):
    def __init__(self, token):
        super().__init__(token)
        if os.path.isfile('polls.pickle'):
            with open('polls.pickle', 'rb') as f:
                self.polls = pickle.load(f)
        else:
            self.polls = dict()
        self.cursor = None
        self.conn = None

    def send_poll(self, *args, **kwargs) -> types.Message:
        result = super(PollBot, self).send_poll(*args, **kwargs)
        self.polls[result.poll.id] = result.poll
        with open('polls.pickle', 'wb') as f:
            pickle.dump(self.polls, f)
        return result

    def clear_polls(self):
        self.polls.clear()
        with open('polls.pickle', 'wb') as f:
            pickle.dump(self.polls, f)
        self.send_message(config.AKIM_ID, 'polls dict was cleared')


bot = PollBot(token=config.TOKEN)


def handle_poll_answer(poll_answer):
    bot.send_message(config.AKIM_ID, f'user_id: {poll_answer.user.id}\n'
                                     f'first_name: {poll_answer.user.first_name}\n'
                                     f'last_name: {poll_answer.user.last_name or "undefined"}\n'
                                     f'username: {"@" + poll_answer.user.username or "undefined"}')
    # all_answers = [option.text for option in bot.polls[poll_answer.poll_id].options]
    # answers = [all_answers[i] for i in poll_answer.option_ids]
    # if len(answers):
    #     bot.send_message(config.AKIM_ID,
    #                      f'{poll_answer.user.first_name}{f" {poll_answer.user.last_name}" or ""} '
    #                      f'voted for {answers} in "{bot.polls[poll_answer.poll_id].question}" poll')
    # else:
    #     bot.send_message(config.AKIM_ID, f'{poll_answer.user.first_name} retracted vote '
    #                                      f'in "{bot.polls[poll_answer.poll_id].question}" poll')


bot.register_poll_answer_handler(handle_poll_answer, None)

if __name__ == '__main__':
    bot.send_message(config.AKIM_ID, 'started')


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


bot.polling(none_stop=True)
