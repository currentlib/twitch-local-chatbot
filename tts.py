from gtts import gTTS
import os
from playsound import playsound
from pygame import mixer
from pynput import keyboard

import time

mixer.init()

pressed = set()

COMBINATIONS = [
    {
        "keys": [
            {keyboard.Key.ctrl_r, keyboard.KeyCode(char="'")},
            {keyboard.Key.ctrl_r, keyboard.KeyCode(char="'")},
        ],
        "command": "skip",
    }
]

def on_press(key):
    pressed.add(key)
    # print(pressed)
    for c in COMBINATIONS:
        for keys in c["keys"]:
            if keys.issubset(pressed):
                mixer.music.stop()
                mixer.music.unload()

def on_release(key):
    if key in pressed:
        pressed.remove(key)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def say(msg, duration, lang):
    audio = gTTS(text=msg, lang=lang)
    audio.save("say.mp3")
    mixer.music.load("say.mp3")
    time_start = time.time()
    mixer.music.play()
    while time.time() < time_start + duration:
        time.sleep(1)
        if not mixer.music.get_busy():
            break
    mixer.music.stop()
    mixer.music.unload()

# def say(msg, duration):
#     t = threading.Thread(target=main_say, args=(msg, duration))
#     t.start()
    

# def welcome(username):
#     myText = "Здоров, " + username + ", як ся маєш?"
#     audio = gTTS(text=myText, lang="uk")
#     audio.save("welcome.mp3")
#     playsound("welcome.mp3")

def say2(msg, duration):
    audio = gTTS(text=msg, lang="uk")
    audio.save("say.mp3")
    playsound("say.mp3")

# say("Довге повідомлення яке теоретично може займати більше ніж три секунди щоб це сказати", 3)
# say("пук", 10)