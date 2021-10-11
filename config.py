import os
from urllib.parse import urlparse

TOKEN = os.environ['BOT_TOKEN']

url = urlparse(os.environ['DATABASE_URL'])
USER = url.username
PASSWORD = url.password
HOSTNAME = url.hostname
DATABASE_NAME = os.environ['DATABASE_NAME']

AKIM_ID = int(os.environ['AKIM_ID'])
MDA_ID = int(os.environ['MDA_ID'])
