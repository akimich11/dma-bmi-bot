from base.decorators import db
import json
import requests


def get_greetings(first_name):
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Origin': 'https://russiannlp.github.io',
        'Referer': 'https://russiannlp.github.io',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cors-site'
    }
    data = {'text': f'{first_name}, с днём рождения! Желаю тебе '}
    url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'

    greeting = requests.post(url, headers=headers, data=json.dumps(data)).json()['predictions']
    short_greeting = greeting.split('\n\n')[0]
    short_greeting = short_greeting[:short_greeting.find('\n')] + short_greeting[short_greeting.find('\n') + 1:]
    return short_greeting


class BirthdayService:
    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_all_birthdays(cursor):
        cursor.execute('SELECT birthday, first_name, last_name, chat_id FROM users u '
                       'JOIN departments d on d.id = u.department_id WHERE birthday IS NOT NULL')

    @staticmethod
    @db.fetch(return_type='value')
    def get_birthday(last_name, cursor):
        cursor.execute('SELECT birthday FROM users WHERE last_name=(%s)', (last_name,))

    @staticmethod
    @db.connect
    def update_next_birthday(last_name, cursor):
        birthday = BirthdayService.get_birthday(last_name)
        if birthday is not None:
            birthday = birthday.replace(birthday.year + 1)
            cursor.execute('UPDATE users SET birthday=(%s) where last_name=(%s)',
                           (birthday, last_name))
