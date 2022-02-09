from base.bot import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Button

from base.decorators import exception_handler, access_checker
from timetable.service import TimetableService
from users.service import UserService

WEEKDAYS = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота')


@bot.message_handler(commands=['timetable'])
@exception_handler
@access_checker(admin_only=False)
def send_timetable_markup(message):
    markup = InlineKeyboardMarkup(row_width=2)
    try:
        command, department_id = message.text.split()
        items = [Button(weekday, callback_data=f'{weekday} {department_id}')
                 for weekday in WEEKDAYS + ('Вся неделя',)]
    except ValueError:
        items = [Button(weekday, callback_data=weekday) for weekday in WEEKDAYS + ('Вся неделя',)]
    markup.add(*items)
    bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: not call.data.startswith('Вся неделя') and ' ' not in call.data)
@exception_handler
@access_checker(admin_only=False)
def send_timetable_for_day(call):
    weekday = call.data
    sub_department = UserService.get_sub_department(call.from_user.id)
    timetable = TimetableService.get_timetable_for_day(sub_department, weekday)
    if timetable is not None:
        message_text = f'Расписание ({weekday}, {sub_department}):\n\n' + \
                        TimetableService.get_pretty_timetable(timetable)
    else:
        message_text = f'{weekday}, {sub_department}: пар нет, повезло-повезло'

    if message_text != call.message.text:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.id,
                              parse_mode='html', reply_markup=None)


@bot.callback_query_handler(func=lambda call: not call.data.startswith('Вся неделя') and ' ' in call.data)
@exception_handler
@access_checker(admin_only=False)
def send_timetable_for_day_by_sub_department(call):
    weekday, sub_department = call.data.split(maxsplit=1)
    sub_department = sub_department.upper()
    sub_department_exists = TimetableService.check_if_sub_department_exists(sub_department)
    if sub_department_exists:
        timetable = TimetableService.get_timetable_for_day(sub_department, weekday)
        if timetable is not None:
            message_text = f'Расписание ({weekday}, {sub_department}):\n\n' + \
                            TimetableService.get_pretty_timetable(timetable)
        else:
            message_text = f'{weekday}, {sub_department}: пар нет, повезло-повезло'
    else:
        message_text = 'Такой группы нет в базе. Либо формат запроса неверный (попробуйте "/timetable КТС")'

    if message_text != call.message.text:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.id,
                              parse_mode='html', reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Вся неделя'))
@exception_handler
@access_checker(admin_only=False)
def send_timetable_for_week(call):
    try:
        department_id = int(call.data.split()[-1])
        sub_department = UserService.get_sub_department(department_id)
    except ValueError:
        department_id, sub_department = UserService.get_departments(call.from_user.id)
    if sub_department is not None:
        timetable = TimetableService.get_timetable_for_week(department_id, sub_department)
        message_text = f'<b>Расписание на неделю ({sub_department})</b>\n\n' + \
                       ''.join([TimetableService.parse_timetable_for_day(timetable, day) for day in WEEKDAYS])
    else:
        message_text = 'Такой группы в базе нет'

    if message_text != call.message.text:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.id,
                              parse_mode='html', reply_markup=None)
