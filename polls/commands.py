from base.bot import bot
from base.decorators.common import exception_handler, access_checker
from base.exceptions import ObjectNotFound
from polls.service import PollService
from users.service import UserService


@bot.message_handler(content_types=['poll'])
@exception_handler
@access_checker(admin_only=False)
def send_poll_copy(message):
    is_admin = UserService.get_is_admin(message.from_user.id)
    if message.chat.id == message.from_user.id and is_admin:
        chat_id = UserService.get_group_chat_id(message.from_user.id)
        poll = message.poll
        bot.send_poll(group_chat_id=chat_id,
                      question=poll.question,
                      options=[option.text for option in poll.options],
                      is_anonymous=False,
                      allows_multiple_answers=poll.allows_multiple_answers
                      )


def send_ignorants_list(message, question=None):
    if question is None:
        question = PollService.get_last_poll_question(message.from_user.id)
    user_id, chat_id = message.from_user.id, message.chat.id
    chat_id = UserService.get_group_chat_id(chat_id) if user_id == chat_id else chat_id
    try:
        ignorants = PollService.get_ignorants_list(chat_id, question)
        if ignorants:
            bot.send_message(message.chat.id, f'Опрос: {question}\n\n'
                                              f'Не проголосовали:\n' +
                             '\n'.join([f'<a href="tg://user?id={user_id}">{first_name} {last_name}</a>'
                                        for user_id, first_name, last_name in ignorants]), parse_mode='html')

        else:
            bot.send_message(message.chat.id, 'Все проголосовали. Горжусь вами!')
    except ObjectNotFound as e:
        bot.send_message(message.chat.id, e)


@bot.message_handler(commands=['tag'])
@exception_handler
@access_checker(admin_only=True)
def tag(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_ignorants_list(message, question=question)
    except ValueError:
        send_ignorants_list(message)


def send_vote_list(message, question=None):
    if question is None:
        question = PollService.get_last_poll_question(message.from_user.id)
    try:
        user_id, chat_id = message.from_user.id, message.chat.id
        chat_id = UserService.get_group_chat_id(chat_id) if user_id == chat_id else chat_id
        options, votes = PollService.get_vote_lists(chat_id, question)
        poll_stats = []
        for option, votes_for_option in zip(options, votes):
            if votes_for_option is not None:
                voters = [f'{last_name} {first_name}' for first_name, last_name in votes_for_option]
                poll_stats.append(f'{option}: {len(voters)}\n<pre>' + '\n'.join(voters) + '</pre>\n')
            else:
                poll_stats.append(f'{option}: 0\n')

        bot.send_message(message.chat.id, f'Опрос: {question}\n\n' + '\n'.join(poll_stats),
                         parse_mode='html')
    except ObjectNotFound:
        bot.send_message(message.chat.id, 'Опрос не найден')


@bot.message_handler(commands=['stats'])
@exception_handler
@access_checker(admin_only=True)
def stats(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_vote_list(message, question)
    except ValueError:
        send_vote_list(message)
