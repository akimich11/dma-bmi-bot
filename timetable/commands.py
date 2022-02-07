from base.bot import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton as Button

from base.decorators.common import exception_handler, access_checker
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
        items = [Button(weekday, callback_data=f'{weekday} {int(department_id)}')
                 for weekday in WEEKDAYS + ('Вся неделя',)]
    except ValueError:
        items = [Button(weekday, callback_data=weekday) for weekday in WEEKDAYS + ('Вся неделя',)]
    markup.add(*items)
    bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: not call.data.startswith('Вся неделя'))
@exception_handler
@access_checker(admin_only=False)
def send_timetable(call):
    try:
        weekday, department_id = call.data.rsplit(maxsplit=1)
        sub_department = UserService.get_sub_department(department_id)
    except ValueError:
        weekday = call.data
        department_id, sub_department = UserService.get_departments(call.from_user.id)
    if sub_department is not None:
        timetable = TimetableService.get_timetable_for_day(department_id, sub_department, weekday)
        if timetable is not None:
            message_text = f'Расписание ({weekday}, {sub_department}):\n\n' + \
                           TimetableService.get_pretty_timetable(timetable)
        else:
            message_text = f'{weekday}, {sub_department}: пар нет, повезло-повезло'

    else:
        message_text = 'Такой группы в базе нет'

    if message_text != call.message.text:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.id,
                              parse_mode='html', reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Вся неделя'))
@exception_handler
@access_checker(admin_only=False)
def send_timetable(call):
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
