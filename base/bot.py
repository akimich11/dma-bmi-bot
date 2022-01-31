from telebot import TeleBot, types
import settings
from polls.service import PollService
from users.service import UserService


class MdaBot(TeleBot):
    def __init__(self, token):
        super().__init__(token)

    def send_poll(self, group_chat_id, *args, **kwargs) -> types.Message:
        result = super(MdaBot, self).send_poll(group_chat_id, *args, **kwargs)
        self.unpin_all_chat_messages(group_chat_id)
        self.pin_chat_message(group_chat_id, result.message_id)
        PollService.create_poll(result.poll, group_chat_id)
        return result

    def handle_poll_answer(self, poll_answer):
        poll_id = poll_answer.poll_id
        user_id = poll_answer.user.id
        user_name = UserService.get_name(user_id)
        poll_question = PollService.get_poll_question(poll_id)

        if poll_question is not None and user_name is not None:
            first_name, last_name = user_name
            poll_options = PollService.get_poll_options(poll_id)
            user_answers = [poll_options[i] for i in poll_answer.option_ids]
            if user_answers:
                self.send_message(settings.AKIM_ID,
                                  f'{first_name} {last_name} '
                                  f'voted for {user_answers} in "{poll_question}" poll')
            else:
                self.send_message(settings.AKIM_ID, f'{first_name} {last_name} retracted vote '
                                                    f'in "{poll_question}" poll')
            PollService.update_poll(poll_id, user_id, user_answers)


bot = MdaBot(token=settings.TOKEN)
bot.register_poll_answer_handler(bot.handle_poll_answer, None)
