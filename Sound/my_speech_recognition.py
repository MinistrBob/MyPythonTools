# pip install SpeechRecognition
# pip install PyAudio

import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as voice:
    print("Say something!")
    audio = r.listen(voice)
    try:
        print("You said: " + r.recognize_google(audio))
    except:
        print("Sorry, I didn't get that!")
