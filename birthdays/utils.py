import json
import urllib.request


def get_greetings(first_name):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/605.1.15 '
                      '(KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Origin': 'https://yandex.ru',
        'Referer': 'https://yandex.ru/',
    }

    api_url = 'https://zeapi.yandex.net/lab/api/yalm/text3'
    payload = {"query": f'{first_name}, с днём рождения! Желаю тебе ', "intro": 0, "filter": 1}
    params = json.dumps(payload).encode('utf8')
    req = urllib.request.Request(api_url, data=params, headers=headers)
    response = urllib.request.urlopen(req)

    greeting = json.loads(response.read().decode('utf8'))['text']
    short_greeting = payload['query'] + greeting.split('\n\n')[0].split('***')[0]
    return short_greeting
