from base.bot import bot
from base.decorators.common import exception_handler, access_checker
from polls.poll_service import PollService
from users.user_service import UserService


@bot.message_handler(content_types=['poll'])
@exception_handler
@access_checker(admin_only=False)
def reply(message):
    is_admin = UserService.get_is_admin(message.from_user.id)
    if message.chat.id > 0 and is_admin:
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
    chat_id = UserService.get_group_chat_id(message.chat.id) if message.chat.id > 0 else message.chat.id
    ignorants = PollService.get_ignorants_list(chat_id, question)
    if ignorants:
        bot.send_message(message.chat.id, f'Не проголосовали:\n' +
                         '\n'.join([
                             f'<a href="tg://user?id={user_id}">{first_name} {last_name}</a>'
                             for user_id, first_name, last_name in ignorants]), parse_mode='html')

    else:
        bot.send_message(message.chat.id, 'Ну либо такого опроса нет, либо все проголосовали')


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
    students, skippers, ignorants = PollService.get_vote_lists(message.from_user.id, question)
    if not students and not skippers and not ignorants:
        bot.send_message(message.chat.id, 'Опрос не найден')
        return

    students = [f'{last_name} {first_name}' for first_name, last_name in students]
    skippers = [f'{last_name} {first_name}' for first_name, last_name in skippers]
    ignorants = [f'<a href="tg://user?id={user_id}">{first_name} {last_name}</a>'
                 for user_id, first_name, last_name in ignorants]

    bot.send_message(message.chat.id,
                     f'Будет: {len(students)}\n<pre>' + '\n'.join(students) + '</pre>\n\n' +
                     f'Не будет: {len(skippers)}\n<pre>' + '\n'.join(skippers) + '</pre>\n\n'
                     f'Непонятно: {len(ignorants)}\n<pre>' + '\n'.join(ignorants) + '</pre>',
                     parse_mode='html')


@bot.message_handler(commands=['stats'])
@exception_handler
@access_checker(admin_only=True)
def poll_stats(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_vote_list(message, question)
    except ValueError:
        send_vote_list(message)
