import time
from datetime import datetime
from dateutil.parser import parse
import json
import random
import webbrowser
import winsound
import re
import os
from responses import RESPONSES

import requests
from lxml import html
from enchant.checker import SpellChecker



SPELL_CHECK = False



spellchecker = SpellChecker("en_US")


primaryCommandPrompt = '>> '
secondaryCommandPrompt = '> '

if os.path.exists('contacts.json'):
    with open('contacts.json','r') as f:
        CONTACTS = json.load(f)
else:
    print("Welcome to virtual-assistant setup, friend")
    CONTACTS = [{"BDAY": None, "GENDER": None, "NN": None, "FULLNAME": None, "EMAIL": None, "PHONE": None}]
    time.sleep(1)
    print("Enter your nickname, or hit return and I'll keep calling you 'friend': ")
    CONTACTS[0]["NN"] = input(primaryCommandPrompt)
    CONTACTS[0]["NN"] = CONTACTS[0]["NN"] if CONTACTS[0]["NN"] != '' else 'friend'
    time.sleep(1)
    print("Okay, %s, here's some guidance:" % CONTACTS[0]["NN"])
    time.sleep(2)
    print(" - At any time, you can tell me more about yourself and change your contact info")
    time.sleep(2)
    print(" - You can tell me your birthday, gender, full name, where you live, and you can also add other contacts")
    time.sleep(2)
    print(" - You can also ask me for help if you get hopelessly lost")
    with open('contacts.json', 'w') as f:
        json.dump(CONTACTS, f)
    time.sleep(1)
    print("Setup complete")
    print()
    time.sleep(1)
    print("Now talk to me!")


class toolBox:
    def __init__(self):
        return

    def sing(self):
        beatlength = 300
        m = random.randint(3,5)
        rand = random.randint(0,1)
        if rand == 0:
            winsound.Beep(200*m,beatlength)
            winsound.Beep(300 * m, beatlength)
            winsound.Beep(400 * m, beatlength)
            winsound.Beep(500 * m, beatlength)
            time.sleep(.5)
            winsound.Beep(300 * m, beatlength)
            winsound.Beep(400 * m, beatlength)
            winsound.Beep(500 * m, beatlength)
            time.sleep(.5)
            winsound.Beep(400 * m, beatlength)
            winsound.Beep(500 * m, beatlength)
            winsound.Beep(600 * m, beatlength)
            time.sleep(.5)
            winsound.Beep(400 * m, beatlength)
            winsound.Beep(300 * m, beatlength)
            winsound.Beep(100 * m, beatlength*2)
        elif rand == 1:
            winsound.Beep(200*m, beatlength)
            winsound.Beep(300*m, beatlength)
            winsound.Beep(400*m, beatlength)
            winsound.Beep(500*m, beatlength)
            winsound.Beep(400*m, beatlength)
            winsound.Beep(300*m, beatlength)
            winsound.Beep(200*m, beatlength)
            winsound.Beep(200*m, beatlength)
            winsound.Beep(300*m, beatlength)
            winsound.Beep(400*m, int(beatlength * 2))

    def thesaurus(self,word):
        url = "http://www.thesaurus.com/browse/%s" % word
        page = requests.get(url)
        tree = html.fromstring(page.content)
        syns = tree.xpath('//div[@class="relevancy-list"]/ul/li/a/span[@class="text"]')
        if syns:
            return ', '.join([d.text_content() for d in syns])
        return random.choice(["Never heard of it", "A %s?" % word])

    def weather(self,*keys):
        appid = 'a98689d8418b0ca737434c67064bb29d'
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=imperial'.format(*self.locationData("latitude","longitude"), appid))
        j = r.json()
        return [eval("%s[%s]" % (j,"][".join(["'%s'" % i if isinstance(i,str) else str(i) for i in k]))) for k in keys]

    def locationData(self,*keys):
        url = 'http://freegeoip.net/json'
        r = requests.get(url)
        j = json.loads(r.text)
        return [j[k] if k in j else None for k in keys]

    def directionsURL(self,to,fro=None):
        if fro is None:
            return 'https://www.google.com/maps/dir/?api=1&destination=%s' % to
        else:
            return 'https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s' % (fro,to)

    def locationURL(self,place):
        return 'https://www.google.com/maps/search/?api=1&query=%s' %place

    def define(self,word,index=None):
        url = "http://www.dictionary.com/browse/%s" % word
        page = requests.get(url)
        tree = html.fromstring(page.content)
        defsets = tree.xpath('//div[@class="def-content"]')
        if defsets:
            defs = [' '.join(d.text_content().replace('\n','').replace('\r','').split()) for d in defsets]
            if index is not None:
                return defs[index]
            else:
                return defs
        return random.choice(["Never heard of it","A %s?" % word])

    def usedInASentence(self,word):
        url = "http://www.dictionary.com/browse/%s" % word
        page = requests.get(url)
        tree = html.fromstring(page.content)
        defsets = tree.xpath('//p[@class="partner-example-text"]')
        if defsets:
            defs = [' '.join(d.text_content().split()) for d in defsets]
            return defs
        return random.choice(["Never heard of it", "A %s?" % word])

    def wikiLookup(self,topic):
        url = "https://en.wikipedia.org/wiki/%s" % topic
        page = requests.get(url)
        tree = html.fromstring(page.content)
        desc = tree.xpath('//div[@class="mw-parser-output"]/p')
        if desc:
            result = desc[0].text_content()
            ul = tree.xpath('//div[@class="mw-parser-output"]/ul')
            if ul:
                result = "%s\n%s" % (result, ul[0].text_content())
            return result

    def personLookup(self,name):
        splitname = name.split()
        for contact in CONTACTS:
            if contact["NN"].lower() == splitname[0].lower() or contact["N"].split()[0].lower() == splitname[0].lower():
                return "%s is in your contacts" % name

        wiki = self.wikiLookup(name)
        if wiki is not None:
            return wiki

        return random.choice(["Never heard of them"])

    def googleIt(self,search):
        webbrowser.open("https://www.google.com/search?q=%s" % search)
        return random.choice(["googling %s" % search,"searching for %s" % search, "accessing interwebs", "okay, NN, I'll google that"])

    def changeContact(self,contactNum,update):
        CONTACTS[contactNum].update(update)
        with open('contacts.json', 'w') as f:
            json.dump(CONTACTS,f)

    def promptYN(self,prompt,failsafe="unsatisfactory answer, retry!",y="y",n="n"):
        print(prompt)
        answer = input(secondaryCommandPrompt).lower()
        if re.match(y,answer):
            return True
        elif re.match(n,answer):
            return False
        else:
            return self.promptYN(failsafe,failsafe,y,n)

    def promptD(self,prompt,failsafe="unsatisfactory answer, retry!"):
        print(prompt)
        answer = input(secondaryCommandPrompt).lower()
        result = []
        for m in re.findall("\d+",answer):
            result.append(int(m))
        if result:
            return result
        else:
            return self.promptD(failsafe,failsafe)


class JERF:
    def __init__(self):
        self.match = None
        self.text = None
        self.toolBox = toolBox()

    def spellcheck(self,text):
        spellchecker.set_text(text)
        for err in spellchecker:
            err.replace(err.suggest()[0] if err.suggest() else err)
        return spellchecker.get_text().lower()

    def contractify(self,text):
        dictionary = {
            " was":"'s",
            " is":"'s",
            " were":"'re",
            " are":"'re",
            " did":"'d"
        }
        regex = r"(\w+)(%s) " % "|".join([d for d in dictionary])
        for m in re.finditer(regex,text):
            text = text.replace(m.group(0),"%s%s " % (m.group(1),dictionary[m.group(2)]))
        return text

    def evaluate(self,text):
        regex = re.compile(r"<eval>(.+?)</eval>",re.DOTALL)
        for m in re.finditer(regex,text):
            result = eval(m.group(1))
            text = text.replace(m.group(0),result if isinstance(result,str) else '')
        regex = re.compile(r"<exec>(.+?)</exec>",re.DOTALL)
        for m in re.finditer(regex, text):
            result = exec(m.group(1))
            text = text.replace(m.group(0),result if isinstance(result,str) else '')
        return text

    def replaceify(self,text):
        replaces = CONTACTS[0]
        for r in replaces:
            text = text.replace(r,replaces[r] if replaces[r] is not None else 'UNKNOWN')
        return text

    def process_reply(self,text_blueprint):
        if isinstance(text_blueprint, tuple):
            return [self.process_reply(part) for part in text_blueprint]
        elif isinstance(text_blueprint, list):
            return self.process_reply(random.choice(text_blueprint))
        return text_blueprint

    def reply(self,text):
        text = self.contractify(self.spellcheck(text.lower()) if SPELL_CHECK else text.lower())
        self.text = text
        for r in RESPONSES:
            self.match = None
            for choice in r["input"]:
                self.match = re.match(choice,text)
                if self.match is not None:
                    rep = ''.join(self.process_reply(r["reply"]))
                    return self.replaceify(self.evaluate(rep))
        return 'say what'


assistant = JERF()

while True:
    text = input(primaryCommandPrompt)
    print(assistant.reply(text))
