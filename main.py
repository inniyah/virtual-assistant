import json
import random
import re
import os
import pickle
import argparse

import requests

import toolbox

home = os.path.expanduser("~")

primaryCommandPrompt = '>> '
secondaryCommandPrompt = '> '

floatRegexNoPlus = r"-?(?:[0-9]*\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[Ee][+\-][0-9]+)?"
floatRegex = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|[0-9]*\.[0-9]+)(?:[Ee]\+[0-9]+)?"


default_contact = {"BDAY": None, "GENDER": None, "NN": None, "FULLNAME": None, "PHONE": None, "EMAILS": []}

currentDir = os.path.dirname(os.path.realpath(__file__))

mtime = os.path.getmtime(os.path.join(currentDir, "responses.py"))

# Load preferences
if os.path.exists(os.path.join(currentDir, "preferences.json")):
    # print("Fetching preferences...")
    with open(os.path.join(currentDir,  "preferences.json"), "r") as f:
        PREFERENCES = json.load(f)

else:
    print("Generating preferences...")
    PREFERENCES = {"contacts":[default_contact], "mtime":mtime, "reminders": [], "musicDir": None}

    if platform.system() == "Darwin":
        PREFERENCES.update({"afplay":False})

    # User initiation
    if __name__ == '__main__':
        print("Welcome to virtual-assistant setup, friend")
        CONTACTS = PREFERENCES["contacts"]
        print("Enter your nickname, or hit return and I'll keep calling you 'friend': ")
        CONTACTS[0]["NN"] = input(secondaryCommandPrompt)
        CONTACTS[0]["NN"] = CONTACTS[0]["NN"] if CONTACTS[0]["NN"] != '' else 'friend'
        print("Okay, %s, here's some guidance:" % CONTACTS[0]["NN"])
        print(" - At any time, you can tell me more about yourself and change your contact info")
        print(" - You can also type 'help' if you get hopelessly lost or want to know what I can do")
        PREFERENCES["contacts"] = CONTACTS
        print("Setup complete")

# Load responses
if os.path.exists(os.path.join(currentDir, 'response_data.p')) and mtime == float(PREFERENCES["mtime"]):
    # print("Fetching response data...")
    with open(os.path.join(currentDir, 'response_data.p'), 'rb') as f:
        RESPONSES = pickle.load(f)

else:
    print("Generating response data...")
    if os.path.exists(os.path.join(currentDir, 'response_data.p')): os.remove(os.path.join(currentDir, 'response_data.p'))
    from responses import RESPONSES,offlineMode
    if not offlineMode:
        with open(os.path.join(currentDir, 'response_data.p'),'wb') as f:
            pickle.dump(RESPONSES,f)
    PREFERENCES["mtime"] = mtime

with open(os.path.join(currentDir, "preferences.json"), "w") as f:
    json.dump(PREFERENCES,f)

CONTACTS = PREFERENCES["contacts"]


toolbox.CONTACTS = CONTACTS
toolbox.PREFERENCES = PREFERENCES


class VirtAssistant:
    def __init__(self, single=False, test=False):
        self.match = None
        self.text = None
        self.test = test
        self.toolBox = toolbox.toolBox(single)

    def float_to_str(self,f):
        s = str(f)
        if s.endswith(".0"): s = s[:-2]
        return s

    def text2num(self, textnum, numwords={}):
        if not numwords:
            units = [
                "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
                "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                "sixteen", "seventeen", "eighteen", "nineteen",
            ]
            tens = ["", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            scales = ["hundred", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion",
                      "sextillion", "septillion","octillion","nonillion","decillion"]

            numwords["and"] = (1, 0)
            for idx, word in enumerate(units):   numwords[word] = (1, idx)
            for idx, word in enumerate(tens):    numwords[word] = (1, idx * 10)
            for idx, word in enumerate(scales):  numwords[word] = (10 ** (idx * 3 or 2), 0)

        # noAnd = ['between','from']

        # pattern = re.compile("(?<=[a-zA-Z])+(-)(?=[a-zA-Z])+")
        # textnum = re.sub(pattern, ' ', textnum)

        # pattern = re.compile("(?!\s)(-)(?!\s)")
        # textnum = re.sub(pattern,' - ',textnum)

        current = result = 0
        stringlist = []
        onnumber = False
        puncs = '|'.join([r"\%s\s?" % p for p in ".,!?;)(@:;"])
        symbols = "|".join(["\{0}+\s?".format(s) for s in "*/+"])
        symbols += r"|\-+\s|(?<=\d)\-+(?=\d)"
        timeRe = r"\d{1,2}:\d{2}"
        split = re.findall(r"({}\s?|{}\s?|{}|{}|\w+['.]?\w*\s?)".format(timeRe, floatRegexNoPlus, puncs, symbols), textnum)

        class Word:
            def __init__(self,origw):
                self.origw = origw
                self.w = self.origw.strip()
                self.ext = ""

        split = [Word(w) for w in split]
        for i,word in enumerate(split):
            if word.w in numwords and not word.w == "and":
                if numwords[word.w][0] == 1 or (numwords[word.w][0] > 1 and i-1 >= 0 and split[i-1].ext in "ni"):
                    ext = "n"
                else:
                    ext = "w"
            elif word == "and":
                if (i-1 >= 0 and split[i-1].ext == "n") and \
                        (i+1 < len(split) and split[i+1].w in numwords) and \
                        (numwords[split[i+1].w][0] < numwords[split[i-1].w][0]):
                    ext = "a"
                else:
                    ext = "w"
            elif ":" not in word.w and (word.w.isdigit() or re.match(floatRegex,word.w)):
                ext = "i"
            else:
                ext = "w"
            split[i].ext = ext

        for i, word in enumerate(split):
            if word.ext in "nai":
                if word.ext == "i":
                    scale, increment = 1, float(word.w)
                else:
                    scale, increment = numwords[word.w]

                lastscale, lastinc = None, None
                if i-1 >= 0 and split[i-1].ext in "ni":
                    if split[i-1].ext == "i":
                        lastscale, lastinc = 1,float(split[i-1].w)
                    else:
                        lastscale, lastinc = numwords[split[i-1].w]

                if lastinc and lastscale and lastinc < 20 and increment < 20 and lastscale == scale == 1:
                    stringlist.append(self.float_to_str(current) + (" " if word.origw.endswith(" ") else ""))
                    current = increment
                else:
                    current = current * scale + increment
                    if scale > 100:
                        result += current
                        current = 0
                onnumber = True
            elif word.ext == "w":
                if onnumber:
                    stringlist.append(self.float_to_str(result + current) + (" " if split[i-1].origw.endswith(" ") else ""))
                stringlist.append(word.origw)
                result = current = 0
                onnumber = False

        if onnumber:
            stringlist.append(self.float_to_str(result + current))

        return ''.join(stringlist)

    def contractify(self,text):
        dictionary = {
            " was":  "'s",
            " is":   "'s",
            " were": "'re",
            " are":  "'re",
            " did":  "'d"
        }
        regex = r"(\w+)(%s) " % "|".join([d for d in dictionary])
        for m in re.finditer(regex,text):
            text = text.replace(m.group(0),"%s%s " % (m.group(1),dictionary[m.group(2)]))
        return text

    def evaluate(self, text):
        print(f"Evaluating: '{text}'")
        regex = re.compile(r"\${(.+?)}",re.DOTALL)
        for m in re.finditer(regex,text):
            result = eval(m.group(1))
            text = text.replace(m.group(0),result if isinstance(result,str) else '')
        regex = re.compile(r"<exec>(.+?)</exec>",re.DOTALL)
        for m in re.finditer(regex, text):
            global_env = globals()
            local_env = locals()
            result = exec(m.group(1), global_env, local_env)
            text = text.replace(m.group(0),result if isinstance(result,str) else '')
        return text

    def replaceify(self,text):
        replaces = CONTACTS[0]
        for r in replaces:
            new = ', '.join(replaces[r]) if isinstance(replaces[r],list) else replaces[r] if replaces[r] is not None else 'UNSPECIFIED'
            text = text.replace(r, new)
        return text

    def process_reply(self,text_blueprint):
        if isinstance(text_blueprint, tuple):
            return [self.process_reply(part) for part in text_blueprint]
        elif isinstance(text_blueprint, list):
            return self.process_reply(random.choice(text_blueprint))
        return text_blueprint

    def reply(self,text,oneline=False):
        text = self.text2num(self.contractify(text))
        if " and " in text and oneline:
            texts = text.split(" and ")
            replies = []
            for t in texts:
                self.text = t
                replies.append(self.reply(t))
            return "\n".join(replies)
        for r in RESPONSES:
            self.match = None
            for choice in r["input"]:
                self.match = re.match(choice, text, re.IGNORECASE)
                if self.match is not None:
                    try:
                        if self.test:
                            return r["reply"]
                        else:
                            rep = ''.join(self.process_reply(r["reply"]))
                            return self.replaceify(self.evaluate(rep))
                    except requests.exceptions.ConnectionError:
                        string = random.choice(["Offline, connection failed","It looks like you're offline, NN",
                                                "I could not connect to the interwebs, NN","Connection failed"])
                        return self.replaceify(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", nargs='*', type=str, default="", help="Run a single command instead of a session.")
    args = parser.parse_args()

    args.cmd = " ".join(args.cmd)

    if len(args.cmd) > 0:
        assistant = VirtAssistant(single=True)
        rep = assistant.reply(args.cmd, oneline=True)
        if rep != '': print(rep)

    else:
        assistant = VirtAssistant()
        while True:
            text = input(primaryCommandPrompt)
            rep = assistant.reply(text)
            if rep != '': print(rep)
