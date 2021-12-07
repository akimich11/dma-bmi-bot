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
