import os
import ctypes
import aiml
import boto3
import time
import speech_recognition as sr
import random
import webbrowser
import urllib.parse
from predicates import BOT_PREDICATES
from googlesearch import search
from sound import Sound
from google import google
from playsound import playsound
from termcolor import colored

speech = sr.Recognizer()
time.ctime()

# list&dictonaries
google_searches_dict = {'what': 'what', 'why': 'why', 'who': 'who', 'which': 'which', 'how': 'how'}
mp3_thankyou_list = ['mp3/whis/thankyou_1.mp3', 'mp3/whis/thankyou_2.mp3']
mp3_listening_problem_list = ['mp3/whis/listening_problem_1.mp3', 'mp3/whis/listening_problem_2.mp3']
mp3_struggling_list = ['mp3/whis/struggling_1.mp3']
mp3_google_search = ['mp3/whis/google_search_1.mp3', 'mp3/whis/google_search_2.mp3']
mp3_open_launch_list = ['mp3/whis/open_1.mp3', 'mp3/whis/open_3.mp3', 'mp3/whis/open_2.mp3']
shut_dict = {'bye': 'bye', 'goodbye': 'goodbye', 'shutdown': 'shutdown', 'stop': 'stop'}

counter = 0

polly = boto3.client('polly')


def titlecard():
    print("\n")
    print('██   ██   ██  ██    ██  ████  ████')
    print('██  ███  ██  ██    ██    ██   ██')
    print('██ ████ ██  ███████    ██    ████')
    print('████  ████  ██    ██    ██        ██')
    print('███     ███  ██    ██  ████   ████')
    print("\n")
    print("=========================================================================")


def get_index(texte):
    if 'first' in texte:
        return 0
    elif 'second' in texte:
        return 1
    elif 'third' in texte:
        return 2
    else:
        return None


def play_sound_from_polly(result, is_google=False):
    global counter
    mp3_name = "output{}.mp3".format(counter)

    obj = polly.synthesize_speech(Text=result, OutputFormat='mp3', VoiceId='Matthew')
    if is_google:
        play_sound(mp3_google_search)

    with open(mp3_name, 'wb') as filet:
        filet.write(obj['AudioStream'].read())
        filet.close()

    playsound(mp3_name)
    os.remove(mp3_name)
    counter += 1


def google_search_result(query):
    search_result = google.search(query.replace('search', ''))

    for result in search_result:
        print(result.description)
        if result.description != '':
            play_sound_from_polly(result.description, is_google=True)
            break


def is_valid_google_search(phrase):
    if google_searches_dict.get(phrase.split(' ')[0]) == phrase.split(' ')[0]:
        return True


def play_sound(mp3_list):
    mp3 = random.choice(mp3_list)
    playsound(mp3)


def read_voice_cmd():
    voice_text = ''
    print('Listening....')

    try:
        with sr.Microphone() as source:
            audio = speech.listen(source=source, timeout=10, phrase_time_limit=5)
        voice_text = speech.recognize_google(audio)
    except sr.UnknownValueError:
        pass

    except sr.RequestError:
        print('Network error.')
    except sr.WaitTimeoutError:
        pass

    return voice_text


def is_valid_note(shut_dict, voice_note):
    for key, value in list(shut_dict.items()):
        try:
            if value == voice_note.split(' ')[0]:
                return True

            elif key == voice_note.split(' ')[1]:
                return True

        except IndexError:
            pass

    return False


BRAIN_FILE = "brain.dump"

k = aiml.Kernel()

if os.path.exists(BRAIN_FILE):
    print("Loading from brain file: " + BRAIN_FILE)
    k.loadBrain(BRAIN_FILE)
else:
    print("Parsing aiml files")
    k.bootstrap(learnFiles="std-startup.aiml", commands="load aiml b")
    print("Saving brain file: " + BRAIN_FILE)
    k.saveBrain(BRAIN_FILE)

for key, val in BOT_PREDICATES.items():
    k.setBotPredicate(key, val)

if __name__ == '__main__':
    titlecard()
    current_hour = time.strptime(time.ctime(time.time())).tm_hour

    if current_hour < 12:
        play_sound_from_polly('Good Morning')
    elif current_hour > 12 and current_hour < 18:
        play_sound_from_polly('Good AfterNoon!')
    elif current_hour >= 18:
        play_sound_from_polly('Good Evening')
    playsound('mp3/whis/greeting.mp3')

while True:

    voice_note = read_voice_cmd().lower()
    print((' >> {}'.format(voice_note)))
    response = k.respond(voice_note)

    if 'search' in voice_note:
        for value in [is_valid_note(google_searches_dict, voice_note)]:
            if is_valid_google_search(voice_note):
                print('searching...')
            playsound('mp3/whis/search_1.mp3')
            google_search_result(voice_note)
            print(colored('for more click at the link below', 'green'))
            play_sound_from_polly('for more click at the link below')
            for url in search(voice_note.replace('search', ''), stop=1):
                print(url)
            continue
    elif 'mute' in voice_note:
        Sound.mute()
        continue
    elif 'volume up' in voice_note:
        Sound.volume_up()
        continue
    elif 'volume down' in voice_note:
        Sound.volume_down()
        continue
    elif 'minimum volume' in voice_note:
        Sound.volume_min()
        continue
    elif 'maximum volume' in voice_note:
        Sound.volume_max()
        continue
    elif 'set volume' in voice_note:
        volume = int(input("Volume (0 - 100): "))
        play_sound_from_polly('Enter the number')
        Sound.volume_set(volume)
        continue
    elif 'open' in voice_note:
        print('opening...')
        start_url = "https://www."
        end_url = ".com"
        urllib.parse.unquote(voice_note)
        play_sound_from_polly('Displaying the result, sir')
        webbrowser.open(start_url + voice_note.replace('open', '').strip() + end_url)
        exit()
    elif 'time' in voice_note:
        ttime = time.strftime('%I:%M%p')
        print(ttime)
        play_sound_from_polly(ttime)
        continue
    elif 'date' in voice_note:
        ddate = time.strftime('%B %d, %Y')
        print(ddate)
        play_sound_from_polly(ddate)
        continue
    elif 'day' in voice_note:
        dday = time.strftime('%A')
        print(dday)
        play_sound_from_polly(dday)
        continue
    elif 'where' in voice_note:
        print('opening...')
        play_sound_from_polly('Displaying the result, sir')
        webbrowser.open("https://www.google.nl/maps/place/" + voice_note + "/&amp;")
        exit()
    elif 'lock' in voice_note and 'unlock' not in voice_note:
        for value in ['windows', 'pc', 'system', 'window']:
            if value in voice_note:
                ctypes.windll.user32.LockWorkStation()
                play_sound_from_polly('System locked sir')
        exit()
    elif 'thank you' in voice_note:
        play_sound(mp3_thankyou_list)
        continue
    elif is_valid_note(shut_dict, voice_note):
        playsound('mp3/whis/bye.mp3')
        exit()

    else:
        if voice_note != '':
            print(response)
            play_sound_from_polly(response)
