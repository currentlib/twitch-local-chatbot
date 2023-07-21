from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio
import json

from datetime import datetime

import database
import tts

with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)
    print("Config read successful")

with open("chat_settings.json", "r") as jsonfile:
    settings = json.load(jsonfile)
    print("Chatcommands read successful")

USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = data["targetChannel"]
APP_ID = data["clientId"]
APP_SECRET = data["clientSecret"]


chat = None
uniqueChatters = []
spam_counters = {
    'between': 0,
    'message_counter': 0
}

async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    await ready_event.chat.join_room(TARGET_CHANNEL)


async def on_message(msg: ChatMessage):
    # print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
    user_info = database.addUser(msg.user.name)
    spam_counters['between']=spam_counters['between']+1
    print(user_info)
    if "тг" in msg.text.lower():
        await chat.send_message(TARGET_CHANNEL, "https://t.me/artshoque_tv")
    last_welcome_hours = (datetime.now()-datetime.strptime(user_info[8], '%Y.%m.%d %H:%M')).total_seconds()/3600
    if last_welcome_hours > settings['welcome_cooldown']:
        tts.say(f"Здоров, {database.getLocalUser(msg.user.name)}, як ся маєш?", 10, 'uk')
        database.setLastWelcome(msg.user.name)
        # uniqueChatters.append(msg.user.name)
    database.incrementMessageCount(msg.user.name)
    if (msg.text[0]=="'"):
        lang = msg.text[1:3]
        sub = 3
        langs = ['uk', 'en', 'pl', 'fr', 'es', 'ja', 'sk', 'ko']
        if lang not in langs:
            lang = 'uk'
            sub = 1
        last_message_seconds = (datetime.now()-datetime.strptime(user_info[7], '%Y.%m.%d %H:%M')).total_seconds()
        if (last_message_seconds>settings['voice_cooldown']):
            tts.say(f"{database.getLocalUser(msg.user.name)}, каже {msg.text[sub:]}", settings['voice_length'], lang)
            database.setLastSay(msg.user.name)
        else:
            await msg.reply(f'Стоп кам. Зачекай ще {str(int(settings["voice_cooldown"]-last_message_seconds))} секунд.')


async def on_reply(cmd: ChatCommand):
    database.addUser(cmd.user.name)
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        print(cmd.parameter)
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')


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



async def run():
    global chat
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(twitch)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.register_command("яє", on_me)
    chat.register_command("скільки", on_howmuch)
    chat.register_command("хтоя", on_whoami)



    chat.start()

    try:
        input('press ENTER to stop\n')
    finally:
        chat.stop()
        await twitch.close()

asyncio.run(run())