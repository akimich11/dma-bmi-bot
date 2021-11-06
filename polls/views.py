import config
from base.bot import bot
from base.decorators.common import exception_handler, admin_only
from polls.models import poll_model


@bot.message_handler(content_types=['poll'])
@exception_handler
@admin_only
def reply(message):
    poll = message.poll
    bot.send_poll(chat_id=config.MDA_ID,
                  question=poll.question,
                  options=[option.text for option in poll.options],
                  is_anonymous=False,
                  allows_multiple_answers=poll.allows_multiple_answers
                  )


def send_ignorants_list(message, department=None, question=None):
    users = poll_model.get_ignorants_list(department, question)
    if users is None:
        bot.send_message(message.chat.id, 'Опрос не найден')
    elif users:
        bot.send_message(message.chat.id, f'Не проголосовали:\n' +
                         '\n'.join([
                             f'<a href="tg://user?id={user.id}">{user.first_name} {user.last_name}</a>'
                             for user in users]), parse_mode='html')

    else:
        bot.send_message(message.chat.id, 'Все проголосовали. Горжусь вами!')


@bot.message_handler(commands=['tag'])
@exception_handler
@admin_only
def tag(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_ignorants_list(message, question=question)
    except ValueError:
        send_ignorants_list(message)


@bot.message_handler(commands=['tag_dma'])
@exception_handler
@admin_only
def tag_dma(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_ignorants_list(message, 'ДМА', question)
    except ValueError:
        send_ignorants_list(message, 'ДМА')


@bot.message_handler(commands=['tag_bmi'])
@exception_handler
@admin_only
def tag_dma(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_ignorants_list(message, 'БМИ', question)
    except ValueError:
        send_ignorants_list(message, 'БМИ')


def send_vote_list(message, question=None, sort_by_department=True):
    students, skippers = poll_model.get_vote_lists(question)
    if students is None:
        bot.send_message(message.chat.id, 'Опрос не найден')
        return
    students = [f'{f"{p:3.0f}%" if isinstance(p, float) else " (+)"} {user.last_name} {user.first_name}'
                for (user, p) in sorted(students,
                                        key=lambda x: (x[0].department[::-1], x[0].last_name) if sort_by_department
                                        else x[0].last_name)]
    skippers = [f'{f"{100 - p:3.0f}%" if isinstance(p, float) else " (-)"} {user.last_name} {user.first_name}'
                for (user, p) in sorted(skippers,
                                        key=lambda x: (x[0].department[::-1], x[0].last_name) if sort_by_department
                                        else x[0].last_name)]

    bot.send_message(message.chat.id, f'Будет: {len(students)}\n<pre>' + '\n'.join(students) + '</pre>\n\n' +
                     f'Не будет: {len(skippers)}\n<pre>' + '\n'.join(skippers) + '</pre>', parse_mode='html')


@bot.message_handler(commands=['stats', 'stats_dma_bmi'])
@exception_handler
@admin_only
def poll_stats(message):
    try:
        command, question = message.text.split(maxsplit=1)
        if command == '/stats':
            send_vote_list(message, question, sort_by_department=False)
        else:
            send_vote_list(message, question)
    except ValueError:
        if message.text.split('@')[0] == '/stats':
            send_vote_list(message, sort_by_department=False)
        else:
            send_vote_list(message)
