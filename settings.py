import os
from urllib.parse import urlparse

TOKEN = os.getenv('BOT_TOKEN', '1934090305:AAEQVPnZer-7TBMEwbTW_1n3pS3PBBELcmg')

MOCK_DATABASE = os.getenv('MOCK_DATABASE', 'True')
if MOCK_DATABASE == 'True':
    DATABASE_USER = 'postgres'
    DATABASE_PASSWORD = 'postgres'
    DATABASE_HOST = '127.0.0.1'
    DATABASE_NAME = 'test'
else:
    url = urlparse(os.getenv('DATABASE_URL'))
    DATABASE_USER = url.username
    DATABASE_PASSWORD = url.password
    DATABASE_HOST = url.hostname
    DATABASE_NAME = os.getenv('DATABASE_NAME')

AKIM_ID = 358160357
