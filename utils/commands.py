import settings
from base.bot import bot
from base.decorators import access_checker
from users.service import UserService


@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message):
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(commands=['register'])
def register_user(message):
    user_data = '\n'.join([f'id: {message.from_user.id}',
                           f'username: @{message.from_user.username}',
                           f'first_name: {message.from_user.first_name}',
                           f'last_name: {message.from_user.last_name}']
                          )
    bot.send_message(settings.SUPERUSER_ID, user_data)
    bot.send_message(message.chat.id, 'Запрос на регистрацию отправлен', reply_to_message_id=message.id)


@bot.message_handler(commands=['group_list', 'group_list_by_departments'])
@access_checker(admin_only=False)
def send_group_list(message):
    order_by_department = 'by_department' in message.text
    users = UserService.get_group_list(message.from_user.id, order_by_department=order_by_department)
    bot.send_message(message.chat.id, f'Список группы {"(по кафедрам)" if order_by_department else ""}:\n' + '\n'.join(
        [f'{i + 1}. {last_name} {first_name}' for i, (last_name, first_name) in enumerate(users)]))
