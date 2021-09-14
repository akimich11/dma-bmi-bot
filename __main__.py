import config
from base.bot import bot
from models.poll_model import poll_model
from models.user_model import user_model
import functools


def admin_only(func):
    @functools.wraps(func)
    def wrapped(message, *args, **kwargs):
        if user_model.users[message.from_user.id].is_admin:
            return func(message, *args, **kwargs)
        else:
            bot.send_message(message.chat.id, 'Команда доступна только старостам')
    return wrapped


@bot.message_handler(commands=['poll_stats'])
@admin_only
def send_stats(message):
    try:
        command, question = message.text.split(maxsplit=1)
        users = poll_model.get_ignorants_list(question)
    except ValueError:
        users = poll_model.get_ignorants_list()
    bot.send_message(message.chat.id, f'Не проголосовали:\n' +
                     '\n'.join([f'<a href="tg://user?id={user.id}">{user.first_name} {user.last_name}</a>'
                                for user in users]), parse_mode='html')


@bot.message_handler(commands=['skips'])
def send_skips(message):
    month, semester = user_model.get_skips(message.from_user.id)
    if isinstance(month, int) and month < 6:
        bot.send_message(message.chat.id, f'Часов за месяц: {month}\n'
                                          f'Часов за семестр: {semester}', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Часов за месяц: {month}\n'
                                          f'Часов за семестр: {semester}\n'
                                          f'Совет: ходи на пары чаще', reply_to_message_id=message.id)


@bot.message_handler(commands=['inc_skips'])
@admin_only
def inc_skips(message):
    try:
        last_names = [last_name.capitalize() for last_name in message.text.split()][1:]
        user_model.inc_skips(last_names)
        bot.send_message(message.chat.id, 'У них стало на 2 часа пропусков больше', reply_to_message_id=message.id)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['new_month'])
@admin_only
def clear_skips(message):
    user_model.clear_skips()
    bot.send_message(message.chat.id, 'Пропуски за месяц обнулены')


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
