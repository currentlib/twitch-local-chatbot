from gtts import gTTS
import os
from playsound import playsound

def welcome(username):
    myText = "Здоров, " + username + ", як ся маєш?"
    audio = gTTS(text=myText, lang="uk")
    audio.save("welcome.mp3")
    playsound("welcome.mp3", block=False)

def say(username, msg):
    myText = f"{username} каже {msg}"
    audio = gTTS(text=myText, lang="uk")
    audio.save("say.mp3")
    playsound("say.mp3", block=False)