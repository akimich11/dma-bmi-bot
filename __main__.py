from datetime import datetime
import time
from threading import Thread

import config
import schedule
from base.bot import bot
from models.poll_model import poll_model
from models.question_model import QuestionModel
from models.user_model import user_model
from decorators.common import exception_handler, admin_only


@bot.message_handler(commands=['make_admin'])
@exception_handler
def make_admin(message):
    try:
        command, last_name = message.text.split()
        if user_model.make_admin(last_name):
            bot.send_message(message.chat.id, 'одним старостой больше')
        else:
            bot.send_message(message.chat.id, 'я такой фамилии не знаю')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['remove_admin'])
@exception_handler
def remove_admin(message):
    try:
        command, last_name = message.text.split()
        if user_model.remove_admin(last_name):
            bot.send_message(message.chat.id, 'одним старостой меньше')
        else:
            bot.send_message(message.chat.id, 'я такой фамилии не знаю')
    except ValueError:
        bot.send_message(message.chat.id, 'wrong format')


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


def send_poll_stats(message, department=None, question=None):
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
        send_poll_stats(message, question=question)
    except ValueError:
        send_poll_stats(message)


@bot.message_handler(commands=['tag_dma'])
@exception_handler
@admin_only
def tag_dma(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_poll_stats(message, 'ДМА', question)
    except ValueError:
        send_poll_stats(message, 'ДМА')


@bot.message_handler(commands=['tag_bmi'])
@exception_handler
@admin_only
def tag_dma(message):
    try:
        command, question = message.text.split(maxsplit=1)
        send_poll_stats(message, 'БМИ', question)
    except ValueError:
        send_poll_stats(message, 'БМИ')


@bot.message_handler(commands=['skips'])
@exception_handler
def send_skips(message):
    month, semester = user_model.get_skips(message.from_user.id)
    if isinstance(month, int) and month < 6:
        bot.send_message(message.chat.id, f'Часов за месяц: {month}\n'
                                          f'Часов за семестр: {semester}',
                         reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Часов за месяц: {month}\n'
                                          f'Часов за семестр: {semester}\n'
                                          f'Совет: ходи на пары чаще',
                         reply_to_message_id=message.id)


@bot.message_handler(commands=['skips_all'])
@exception_handler
def send_skips_all(message):
    data = []
    for user in user_model.users.values():
        month, semester = user_model.get_skips(user.id)
        data.append(f'{month: 2d} {semester: 3d}  {user.first_name} {user.last_name}')
    bot.send_message(message.chat.id, 'Таблица пропусков\n\n<pre>' + '\n'.join(data) + '</pre>', parse_mode='html')


@bot.message_handler(commands=['inc_skips'])
@exception_handler
@admin_only
def inc_skips(message):
    try:
        last_names = [last_name.capitalize() for last_name in
                      message.text.split()][1:]
        user_model.inc_skips(last_names)
        bot.send_message(message.chat.id,
                         'У них стало на 2 часа пропусков больше',
                         reply_to_message_id=message.id)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['set_skips'])
@exception_handler
@admin_only
def set_skips(message):
    try:
        last_name, month, semester = [last_name.capitalize() for last_name in
                                      message.text.split()][1:]
        user_model.set_skips(last_name, int(month), int(semester))
        bot.send_message(message.chat.id,
                         f'Теперь пропусков {month} за месяц и {semester} за семестр',
                         reply_to_message_id=message.id)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'wrong format')


@exception_handler
def clear_skips():
    user_model.clear_skips()
    bot.send_message(config.MDA_ID, 'Пропуски за месяц обнулены')


@exception_handler
def schedule_check():
    while True:
        schedule.run_pending()
        time.sleep(30)


@exception_handler
def send_periodic_question(question):
    bot.send_poll(chat_id=config.MDA_ID,
                  question=f'{question.question} {datetime.utcnow().day}.{datetime.utcnow().month}',
                  options=question.options,
                  is_anonymous=False,
                  allows_multiple_answers=question.is_multi
                  )


if __name__ == '__main__':
    for q in QuestionModel().questions:
        getattr(schedule.every(), q.weekday
                ).at(q.time).do(send_periodic_question, question=q)
    # schedule.every(31).days.at('07:00').do(clear_skips)

    Thread(target=schedule_check).start()
    bot.send_message(config.AKIM_ID, 'started')

bot.polling(none_stop=True)
