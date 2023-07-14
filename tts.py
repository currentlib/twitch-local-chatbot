from gtts import gTTS
import os
from playsound import playsound

def welcome(username):
    myText = "Здоров, " + username + ", як ся маєш?"
    audio = gTTS(text=myText, lang="uk", slow=False, )
    audio.save("welcome.mp3")
    playsound("welcome.mp3")