from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio
import json

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
    # if 
    if "тг" in msg.text.lower():
        await chat.send_message(TARGET_CHANNEL, "https://t.me/artshoque_tv")
    if not msg.user.name in uniqueChatters:
        tts.welcome(msg.user.name)
        uniqueChatters.append(msg.user.name)


async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        print(cmd.parameter)
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')


async def run():
    global chat
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(twitch)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.register_event(ChatEvent.SUB, on_sub)

    chat.register_command('reply', globals()["test_command"])

    chat.start()

    try:
        input('press ENTER to stop\n')
    finally:
        chat.stop()
        await twitch.close()

asyncio.run(run())