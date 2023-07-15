from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio
import json

import database
import tts

with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    print("Config read successful")

with open("chatcommands.json", "r") as jsonfile:
    commands = json.load(jsonfile)
    print("Chatcommands read successful")

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = data["targetChannel"]
APP_ID = data["clientId"]
APP_SECRET = data["clientSecret"]


chat = None
uniqueChatters = []


async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    await ready_event.chat.join_room(TARGET_CHANNEL)


async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
    database.addUser(msg.user.name)
    if "тг" in msg.text.lower():
        await chat.send_message(TARGET_CHANNEL, "https://t.me/artshoque_tv")
    if not msg.user.name in uniqueChatters:
        tts.welcome(database.getLocalUser(msg.user.name))
        uniqueChatters.append(msg.user.name)
    database.incrementMessageCount(msg.user.name)
    if msg.text[:2]=="! ":
        say_plain(msg.user.name, msg.text)


async def on_reply(cmd: ChatCommand):
    database.addUser(cmd.user.name)
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        print(cmd.parameter)
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def on_say(cmd: ChatCommand):
    database.addUser(cmd.user.name)
    if len(cmd.parameter) == 0:
        await cmd.reply('ти не написав мені, що сказати')
    else:
        tts.say(database.getLocalUser(cmd.user.name), cmd.parameter)
        # await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

def say_plain(user, msg):
    database.addUser(user)
    tts.say(database.getLocalUser(user), msg)
        # await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def on_me(cmd: ChatCommand):
    database.addUser(cmd.user.name)
    if len(cmd.parameter) == 0:
        await cmd.reply('ти не сказав мені, як тебе називати. Тепер ти будеш "Пісюн"')
        database.setLocalUser(cmd.user.name, "Пісюн")
    else:
        database.setLocalUser(cmd.user.name, cmd.parameter)
        await cmd.reply(f'Тепер я тебе буду називати {cmd.parameter}')

async def on_howmuch(cmd: ChatCommand):
    database.addUser(cmd.user.name)
    count = database.getMessageCount(cmd.user.name)
    await cmd.reply(f"Ти написав вже {count} повідомлень.")

async def on_whoami(cmd: ChatCommand):
    database.addUser(cmd.user.name)
    await cmd.reply(f"Ти назвав себе {database.getLocalUser(cmd.user.name)}")

# Custom functions goes here

async def on_random(cmd: ChatCommand, isParam: bool, sender, target, parameter):
    if (len(cmd.parameter) == 0) and (isParam == True):
        await cmd.reply('не бачу аргументу, не можу виконати цю команду')
    else:
        await cmd.reply

async def run():
    global chat
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(twitch)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.register_command("скажи", on_say)
    chat.register_command("я", on_me)
    chat.register_command("скільки", on_howmuch)
    chat.register_command("хтоя", on_whoami)
    

    for command in commands["commands"]:
        if command["mode"] == "replyCommand":
            for trigger in command["triggers"]:
                chat.register_command(trigger, on_reply)
        # if command["mode"] == "random":
        #     for trigger in command["triggers"]:
        #         chat.register_command(trigger, on_random)
        # if command["mode"] == "random_par":
        #     for trigger in command["triggers"]:
        #         chat.register_command(trigger, on_random_par)



    chat.start()

    try:
        input('press ENTER to stop\n')
    finally:
        chat.stop()
        await twitch.close()

asyncio.run(run())