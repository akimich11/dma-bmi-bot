from base.bot import bot
from base.decorators import exception_handler, access_checker
from skips.service import SkipsService
from users.service import UserService


@bot.message_handler(commands=['skips'])
@exception_handler
@access_checker(admin_only=False)
def send_skips(message):
    month, semester = SkipsService.get_skips(message.from_user.id)
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
@access_checker(admin_only=False)
def send_skips_all(message):
    data = []
    user_id, chat_id = message.from_user.id, message.chat.id
    chat_id = UserService.get_group_chat_id(chat_id) if user_id == chat_id else chat_id
    skips_all = SkipsService.get_all_skips(chat_id)

    for first_name, last_name, month, semester in skips_all:
        data.append(f'{month: 2d} {semester: 3d}  {first_name} {last_name}')
    bot.send_message(message.chat.id, 'Таблица пропусков\n\n<pre>' + '\n'.join(data) + '</pre>', parse_mode='html')


@bot.message_handler(commands=['inc_skips'])
@exception_handler
@access_checker(admin_only=True)
def inc_skips(message):
    try:
        last_names = [last_name.capitalize() for last_name in message.text.split()][1:]
        SkipsService.inc_skips(last_names)
        bot.send_message(message.chat.id, 'У них стало на 2 часа пропусков больше',
                         reply_to_message_id=message.id)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'wrong format')


@bot.message_handler(commands=['set_skips'])
@exception_handler
@access_checker(admin_only=True)
def set_skips(message):
    try:
        last_name, month, semester = [last_name.capitalize() for last_name in message.text.split()][1:]
        SkipsService.set_skips(last_name, int(month), int(semester))
        bot.send_message(message.chat.id,
                         f'Теперь пропусков {month} за месяц и {semester} за семестр',
                         reply_to_message_id=message.id)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'wrong format')


def clear_skips():
    data = SkipsService.clear_skips()
    for department, chat_id in data:
        bot.send_message(chat_id, f'Пропуски кафедры {department} за месяц обнулены')


@bot.message_handler(commands=['new_month'])
@exception_handler
@access_checker(admin_only=True)
def clear(message):
    clear_skips()
