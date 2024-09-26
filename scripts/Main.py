# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests, json, time, random, numpy, sys

#Load JSON Files
PersonalFile = json.load(open("jsons/Personal.json", "r"))
MusicFile = json.load(open("jsons/Music.json", "r"))
RandomFile = json.load(open("jsons/Random.json", "r"))
PhrasesFile = json.load(open("jsons/Phrases.json", "r"))

#Variables
Today = time.strftime("%Y-%m")
ChristmasNegativePhrases = PhrasesFile["Christmas"]["No"] + PhrasesFile["No"]
ChristmasPositivePhrases = PhrasesFile["Christmas"]["Yes"] + PhrasesFile["Yes"]
BirthdayNegativePhrases = PhrasesFile["Birthday"]["No"] + PhrasesFile["No"]
BirthdayPositivePhrases = PhrasesFile["Birthday"]["Yes"] + PhrasesFile["Yes"]

#Functions
def Choose(list):
  return random.choice(list)

def RequestApi(url):
  return requests.get(url=url).json()

#Magic from stackoverflow
def to_json(o, level=0):
  ret = ""
  if isinstance(o, dict):
    ret += "{" + "\n"
    comma = ""
    for k, v in o.items():
      ret += comma
      comma = ",\n"
      ret += " " * 3 * (level + 1)
      ret += '"' + str(k) + '":' + " "
      ret += to_json(v, level + 1)

    ret += "\n" + " " * 3 * level + "}"
  elif isinstance(o, str):
    ret += '"' + o + '"'
  elif isinstance(o, list):
    ret += "[" + ",".join([to_json(e, level + 1) for e in o]) + "]"
  elif isinstance(o, tuple):
    ret += "[" + ",".join(to_json(e, level + 1) for e in o) + "]"
  elif isinstance(o, bool):
    ret += "true" if o else "false"
  elif isinstance(o, int):
    ret += str(o)
  elif isinstance(o, float):
    ret += '%.7g' % o
  elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.integer):
    ret += "[" + ','.join(map(str, o.flatten().tolist())) + "]"
  elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.inexact):
    ret += "[" + ','.join(map(lambda x: '%.7g' % x, o.flatten().tolist())) + "]"
  elif o is None:
    ret += 'null'
  else:
    raise TypeError("Unknown type '%s' for json serialization" % str(type(o)))
  return ret

#Cool things
RandomFile['RandomStuff']["IsTodayChristmas?"] = Choose(ChristmasPositivePhrases) if Today == "25-12" else Choose(ChristmasNegativePhrases)
RandomFile['RandomStuff']["IsTodayMyBirthday?"] = Choose(BirthdayPositivePhrases) if Today == "07-09" else Choose(BirthdayNegativePhrases)

try: RandomFile['RandomStuff']["FunFactOfTheDay"] = RequestApi("https://uselessfacts.jsph.pl/random.json?language=en")['text'].replace('"', "'").replace('\n', ' ').replace('\r', '').replace('\n', ' ').replace('\r', '')
except Exception as error:
  print("FunFactOfTheDay error: " + str(error))
  RandomFile['RandomStuff']["FunFactOfTheDay"] = Choose(PhrasesFile["ErrorMessages"])

try: RandomFile['RandomStuff']["CoolAdviceOfTheDay"] = RequestApi("https://api.adviceslip.com/advice")['slip']['advice'].replace('"', "'").replace('\n', ' ').replace('\r', '')
except Exception as error:
  print("CoolAdviceOfTheDay error: " + str(error))
  RandomFile['RandomStuff']["CoolAdviceOfTheDay"] = Choose(PhrasesFile["ErrorMessages"])

try: RandomFile['RandomStuff']["DadJokeOfTheDay"] = RequestApi("https://icanhazdadjoke.com/slack")['attachments'][0]['text'].replace('"', "'").replace('\n', ' ').replace('\r', '')
except Exception as error:
  print("DadJokeOfTheDay error: " + str(error))
  RandomFile['RandomStuff']["DadJokeOfTheDay"] = Choose(PhrasesFile["ErrorMessages"])

'''
not needed anymore
try: PersonalFile['Will']["CurrentStackOverflowReputation"] = RequestApi("https://stackoverflow.com/users/flair/12368797.json")["reputation"].replace('"', "'")
except Exception as error:
  print("CurrentStackOverflowReputation error: " + str(error))
  PersonalFile['Will']["CurrentStackOverflowReputation"] = Choose(PhrasesFile["ErrorMessages"])
'''

try: 

  MemeList = [meme['id'] for meme in RequestApi("https://api.imgflip.com/get_memes")['data']['memes']]
  JokeRequest = RequestApi("https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun,Spooky,Christmas?blacklistFlags=nsfw,religious,political,racist,sexist,explicit")

  RandomFile['RandomStuff']["RandomMemeOfTheDay"] = requests.post("https://api.imgflip.com/caption_image", data={
  "template_id": Choose(MemeList),
  "username": sys.argv[1],
  "password": sys.argv[2],
  "text0": JokeRequest['setup'] if 'setup' in JokeRequest else JokeRequest['joke'],
  "text1": JokeRequest['delivery'] if 'delivery' in JokeRequest else " "
  }).json()['data']['url']

except Exception as error:
  print("RandomMemeOfTheDay error: " + str(error))
  RandomFile['RandomStuff']["RandomMemeOfTheDay"] = Choose(PhrasesFile["ErrorMessages"])

PersonalFile["Will"]["Favorites"]["Music"] = MusicFile #One day it will be real stats from the spotify API

#Create prettified Json
will = dict(list(PersonalFile.items()) + list(RandomFile.items()))

MyData = "\n```json\n" + to_json(will) + "\n```"

#Append new data to the README.md file
with open('README.md', 'r', encoding="utf8") as file:
    
    data = file.read().splitlines()

    start = data.index("<!--START_SECTION:mydata-->") + 1
    end = data.index("<!--END_SECTION:mydata-->") - 1

    DataTowrite = data[:start] + MyData.splitlines() + data[end:]

    with open('README.md', 'w', encoding="utf8") as OutFile:
      for item in DataTowrite:
        OutFile.write("%s\n" % item)
