import atexit
import os
import settings
from base.bot import bot
from base.db import ConnectionMixin
from schedules.service import ScheduleService
from users.service import UserService


MDA_ID = os.getenv('MDA_ID', 270241310)


@bot.message_handler(content_types=['text', 'photo', 'sticker', 'animation',
                                    'audio', 'document', 'video', 'voice', 'poll', 'location', 'video_note'])
def forward_message(message):
    _, last_name = UserService.get_name(message.from_user.id)
    if last_name in [
        "Буйвал", "Войтко", "Денгалёв", "Кацуба", "Коган", "Кузьмицкий", "Кураш", "Кучин",
        "Лукашевич", "Макаровец", "Малыщик", "Мясоеденков", "Новиков",
        "Прохоров", "Рогожников", "Сечко", "Суравежкин", "Филинович", "Филипович", "Шпилевский", "Яцевич"
    ] and message.chat.id != MDA_ID:
        bot.copy_message(MDA_ID, message.chat.id, message.id)
        bot.send_message(message.chat.id, 'Сообщение переслано', reply_to_message_id=message.id)


if __name__ == '__main__':
    ScheduleService.init_schedule()
    bot.send_message(settings.SUPERUSER_ID, 'started')

atexit.register(ConnectionMixin.conn.close)
bot.polling(none_stop=True)
