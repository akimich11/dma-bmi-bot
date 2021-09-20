from telebot import TeleBot, types
import config
from models.user_model import user_model
from models.poll_model import poll_model


class MdaBot(TeleBot):
    def __init__(self, token):
        super().__init__(token)

    def send_poll(self, *args, **kwargs) -> types.Message:
        result = super(MdaBot, self).send_poll(*args, **kwargs)
        poll_model.add_poll(result.poll)
        return result

    def handle_poll_answer(self, poll_answer):
        if poll_answer.poll_id in poll_model.polls and poll_answer.user.id in user_model.users:
            poll, votes = poll_model.polls[poll_answer.poll_id]
            user = user_model.users[poll_answer.user.id]
            all_answers = [option.text for option in poll.options]
            user_answers = [all_answers[i] for i in poll_answer.option_ids]
            if user_answers:
                self.send_message(config.AKIM_ID,
                                  f'{user.first_name} {user.last_name} '
                                  f'voted for {user_answers} in "{poll.question}" poll')
                votes[user.id] = user_answers
            else:
                self.send_message(config.AKIM_ID, f'{user.first_name} {user.last_name} retracted vote '
                                                  f'in "{poll.question}" poll')
                del votes[user.id]
            poll_model.update_poll(poll, votes)


bot = MdaBot(token=config.TOKEN)
bot.register_poll_answer_handler(bot.handle_poll_answer, None)
