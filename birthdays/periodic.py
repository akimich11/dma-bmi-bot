import datetime
from birthdays.views import send_greetings
from users.models import user_model


def check_birthdays():
    for user in user_model.users.values():
        if user.birthday == datetime.datetime.now().date():
            send_greetings(user.first_name)
            user_model.update_next_birthday(user)
