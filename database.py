import sqlite3
from datetime import datetime

con = sqlite3.connect("database.db", check_same_thread=False)

cur = con.cursor()

def isUserAdded(user):
    res = cur.execute(f"SELECT username_twitch FROM users WHERE username_twitch='{user}';")
    return len(res.fetchall()) == 1

def addUser(user):
    if not isUserAdded(user):
        now = datetime.now()
        cur.execute(f"INSERT INTO users (username_twitch, username_local, is_changeable, first_message, message_count, is_limited, last_message, last_say, last_welcome) VALUES ('{user}', '{user}', True, '{now.strftime('%Y.%m.%d %H:%M')}', 0, 1, '', '{now.strftime('%Y.%m.%d %H:%M')}'), '2023.07.01 00:00';")
        con.commit()
    return getUser(user)[0]

def getUser(user):
    res = cur.execute(f"SELECT * FROM users WHERE username_twitch='{user}';")
    return res.fetchall()

def setLocalUser(user, local_username):
    user_data = getUser(user)[0]
    if user_data[2]==1:
        cur.execute(f"UPDATE users SET username_local='{local_username}', last_message='{datetime.now().strftime('%Y.%m.%d %H:%M')}' WHERE username_twitch='{user}'")
        con.commit()
    else:
        print("User is not changeable.")

def getLocalUser(user):
    res = getUser(user)
    return res[0][1]

def incrementMessageCount(user):
    res = getUser(user)
    newCount = res[0][4]+1
    cur.execute(f"UPDATE users SET message_count='{newCount}' WHERE username_twitch='{user}'")
    con.commit()

def getMessageCount(user):
    res = getUser(user)
    return res[0][4]

def setLastSay(user):
    user_data = getUser(user)[0]
    cur.execute(f"UPDATE users SET last_say='{datetime.now().strftime('%Y.%m.%d %H:%M')}' WHERE username_twitch='{user}'")
    con.commit()

def setLastWelcome(user):
    user_data = getUser(user)[0]
    cur.execute(f"UPDATE users SET last_welcome='{datetime.now().strftime('%Y.%m.%d %H:%M')}' WHERE username_twitch='{user}'")
    con.commit()

# addUser("Aaaartshoque")
# setLocalUser("artshoque", "Софія")
# print(getLocalUser("cymbuk"))