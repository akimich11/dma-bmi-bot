import config
import mysql.connector

with open('../users.csv') as f:
    users = [line.strip('\n').split(',') for line in f.readlines()]

conn = mysql.connector.connect(host=config.HOSTNAME, database=config.DATABASE_NAME,
                               user=config.USER, password=config.PASSWORD)
conn.autocommit = True
cursor = conn.cursor(buffered=True)

for user in users:
    insert_user = (
        int(user[0]), user[1], user[3], user[2], user[4],
        user[5] == 'True', user[6] == 'True', int(user[7]))
    cursor.execute("""INSERT IGNORE INTO users VALUES (%s,%s,%s,%s,%s,%s, %s, %s, default, default)""", insert_user)

cursor.close()
conn.close()
