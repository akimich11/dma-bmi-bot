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
        items = [Button(weekday, callback_data=f'{weekday} {int(department_id)}') for weekday in WEEKDAYS + ('Вся неделя',)]
    except ValueError:
        items = [Button(weekday, callback_data=weekday) for weekday in WEEKDAYS + ('Вся неделя',)]
    markup.add(*items)
    bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] != 'Вся неделя')
@exception_handler
@access_checker(admin_only=False)
def send_timetable(call):
    data = call.data.split()
    weekday = data[0]
    if len(data) == 2:
        department_id = data[1]
        sub_department = UserService.get_sub_department(department_id)
    else:
        department_id, sub_department = UserService.get_departments(call.from_user.id)
    timetable = TimetableService.get_timetable_for_day(department_id, sub_department, weekday)
    if timetable is None:
        bot.edit_message_text(f'{weekday}, {sub_department}: пар нет, повезло-повезло',
                              call.message.chat.id, call.message.id, reply_markup=None)
    else:
        message_text = f'Расписание ({weekday}, {sub_department}):\n\n<pre>' + \
                       '\n'.join([f'{time:%H:%M} | {subject:^5.5} | {subject_type} | {auditory}'
                                  for time, subject, subject_type, auditory in timetable]) + '</pre>'
        if message_text != call.message.text:
            bot.edit_message_text(message_text, call.message.chat.id, call.message.id,
                                  parse_mode='html', reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'Вся неделя')
@exception_handler
@access_checker(admin_only=False)
def send_timetable(call):
    data = call.data.split()
    if data == 2:
        department_id = data[1]
        sub_department = UserService.get_sub_department(department_id)
    else:
        department_id, sub_department = UserService.get_departments(call.from_user.id)

    timetable = TimetableService.get_timetable_for_week(department_id, sub_department)

    message_text = f'<b>Расписание на неделю ({sub_department})</b>\n\n' + \
                   ''.join([TimetableService.parse_timetable_for_day(timetable, day) for day in WEEKDAYS])
    if message_text != call.message.text:
        bot.edit_message_text(message_text, call.message.chat.id, call.message.id,
                              parse_mode='html', reply_markup=None)
