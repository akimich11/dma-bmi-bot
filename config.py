import os
from urllib.parse import urlparse

TOKEN = os.environ.get('BOT_TOKEN', '1934090305:AAEQVPnZer-7TBMEwbTW_1n3pS3PBBELcmg')

url = urlparse(os.environ.get('DATABASE_URL',
                              'mysql://bfef7aadad645a:474c1212@eu-cdbr-west-02.cleardb.net/heroku_8a3c9b189c23311'
                              '?reconnect=true'))
USER = url.username
PASSWORD = url.password
HOSTNAME = url.hostname
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'heroku_8a3c9b189c23311')

AKIM_ID = os.environ.get('AKIM_ID', 270241310)
MDA_ID = os.environ.get('MDA_ID', 270241310)
