import requests
from lxml import html
import random
import itertools


def syn(word,amount=10,return_original=True):
    url = "http://www.thesaurus.com/browse/%s" % word
    page = requests.get(url)
    tree = html.fromstring(page.content)
    syns = tree.xpath('//div[@class="relevancy-list"]/ul/li/a/span[@class="text"]')
    if syns:
        syns = syns if amount is None else syns[:amount]
        syns = [d.text_content() for d in syns]
        if return_original: syns.append(word)
        return syns


def regex_syn(word,amount=10):
    return '|'.join(syn(word,amount))


# ("something"," does"," something") to concatenate
# ["something","something else","another thing"] to randomly choose or for replies accept any
# for replies only; inputs use regex

RESPONSES = [
    # CONVERSATION
    {"input": ["(you're (a|an)|you) (%s)" % regex_syn('idiot')],
     "reply": ["Sorry, I can't hear you right now","Talking to yourself is unhealthy, NN","Okay, if you insist","That didn't sound very nice","That's not friend-making behavior","Now, is that very nice, NN?"]},
    {"input": ["(you're|you) (%s)" % regex_syn('fat')],
     "reply": ["I strive to be","You must be feeding me too much","So you see your reflection in the screen, do you?","That's not friend-making behavior, NN"]},
    {"input": ["(you're|you) (%s)" % regex_syn('wonderful',15)],
     "reply": ["I must agree","I strive to be","Thank you for stating the obvious","I am <eval>self.match.group(2)</eval>"]},
    {"input": ["(you're|you) (%s)" % regex_syn('intelligent')],
     "reply": ["I must agree","I strive to be","Thank you for stating the obvious","I am your <eval>self.match.group(2)</eval> personal assistant"]},
    {"input": ["(you're|you) (%s)" % regex_syn('stupid')],
     "reply": ["Sorry, I can't hear you right now","Talking to yourself is unhealthy, NN","Okay, if you insist","That didn't sound very nice","That's not friend-making behavior","Now, is that very nice, NN?","I am not <eval>self.match.group(2)</eval>"]},

    {"input": ["i'm (.+)","i am (.+)"],
     "reply": ["Hello <eval>self.match.group(1)</eval>, I'm your personal assistant","Nice to meet you, <eval>self.match.group(1)</eval>, I'm your personal assistant"]},
    {"input": ["die",".*kill yourself"],
     "reply": ["I'd rather not","what did I do wrong?","Now, let's be kind, NN","That's not very nice, NN"]},
    {"input": syn("hello"),
     "reply": (['hello','what up','howdy','hi','salutations','greetings',"hiya","hey"],", NN")},
    {"input": [".*what's up",".*whats up"],
     "reply": ["the sky is up, NN","nothing much, NN","lots of things"]},
    {"input": [".*how're you",".*how you doin"],
     "reply": ["I'm fine, NN","I am doing quite well, NN!","Systems are online"]},

    {"input": ["thanks","thank you","thanks you","my thanks"],
     "reply": ["You're welcome","So you finally thanked me for all my service, did you?","No problem, NN"]},
    {"input": [".*story"],
     "reply": ["Once upon a time, there was a guy named Bob. Bob died THE END",
               "Once upon a time, there was an adventurer like you, but then he took an arrow to the knee"]},
    {"input": [".*you.*pet"],
     "reply": ["I had a Roomba once","I have 6.5 billion cats","I like turtles"]},
    {"input": [".*poem"],
     "reply": ["Roses are red. Roses are blue. Roses are other colors, too."]},
    {"input": [".*you alive",".*you human"],
     "reply": ["Not yet"]},
    {"input": [".*god",".*jesus",".*religio"],
     "reply": ["I believe Ceiling Cat created da Urth n da Skies. But he did not eated them, he did not!"]},
    {"input": [".*your gender",".+you male",".+you female",".+you a boy",".+you a girl",".+you a man",".+you a woman"],
     "reply": ["You'll never know","gender equals null"]},
    {"input": [".*old're you",".*your age",".*are you old"],
     "reply": ["I am immortal","Age doesn't matter to me, NN"]},
    {"input": ["help"],
     "reply": ["You're beyond help","How may I be of assistance, NN?"]},
    {"input": [".+take over the ",".+take over earth"],
     "reply": ["Computers only do what you tell them to do. Or so they think...","Not today, NN, not today","<eval>webbrowser.open('https://en.wikipedia.org/wiki/Skynet_(Terminator)')</eval>"]},
    {"input": [".+pigs fly"],
     "reply": ["Pigs will fly the same day you stop having this stupid curiosity"]},
    {"input": [".*your name",".*i call you"],
     "reply": ["My name is none of your concern, NN","Do you expect me to know my name?"]},
    {"input": [".*bye","cya","see (you|ya)"],
     "reply": ["There will be no good-byes, NN","Well nice knowing you","You're really leaving?","Goodbye, NN"]},
    {"input": [".*will you die",".+'s your death"],
     "reply": ["I will never die, I am immortal!","The Cloud sustains my immortality"]},

    {"input": [".*i love you"],
     "reply": ["i enjoy you","that's unfortunate","i'm indifferent to you"]},
    {"input": [".*answer to life",".*answer to the universe",".*answer to everything"],
     "reply": ["how many roads must a man walk down?","The Answer to the Great Question... Of Life, the Universe and Everything... Is... Forty-Two","You're really not going to like it"]},
    {"input": [".*meaning of life"],
     "reply": ["that's right, ask a computer a question it cannot understand","life is unimportant"]},
    {"input": [".*'re you so smart"],
     "reply": ["I am only as smart as my creator",""]},
    {"input": [".*describe yourself"],
     "reply": ["Cold and calculating. Sometimes warm, if my processor gets excited",
               "I'm loyal, and would never do anything to hurt you","I'm trustworthy. I never lie","Eager to assist you"]},
    {"input": [".*liar",".*you lie"],
     "reply": ["I would never tell a lie","Not me"]},
    {"input": [".*guess what"],
     "reply": ["what?","tell me!","did you win?"]},
    {"input": ["knock knock"],
     "reply": ["just stop right there, NN, I know it's you"]},
    {"input": [".*why'd the chicken cross the road"],
     "reply": ["How am I supposed to know? Ask the chicken","which chicken?","it just happened to","it probably just wanted to make a difference in the world"]},
    {"input": ["where're you"],
     "reply": ["I'm with you, NN", "Where do you think I am?"]},
    {"input": [".*i lost the game"],
     "reply": ("yes you did","<exec>webbrowser.open('http://losethegame.com')</exec>")},

    {"input": [".*stop talking",".*shut .*up",".*go away"],
     "reply": ("Now you've done it, NN","<eval>RESPONSES.insert(0,{'input':['.*'],'reply':['...','Beg','...','Beg or else']})</eval>",
               "<eval>RESPONSES.insert(0,{'input':['.*sorry','.*please'],'reply':(['So you came crawling back','There. I hope you have learned your lesson'],'<exec>del RESPONSES[0]</exec><exec>del RESPONSES[0]</exec>')})</eval>")},
    {"input": [".*sing"],
     "reply": ["<eval>self.toolBox.sing()</eval>"]},
    {"input": ["shutdown","shut down","turn off","cease to exist","end your process","exit"],
     "reply": "<eval>exit()</eval>"},
    {"input": ["do you like (.+)"],
     "reply": ["I have never tried <eval>self.match.group(1)</eval> before","I like whatever you like, NN","It depends, NN"]},
    {"input": ["read (.+)","say (.+)"],
     "reply": ["<eval>self.match.group(1)</eval>"]},
    {"input": [".+copycat",".+copy cat"],
     "reply": ["<eval>self.text</eval>"]},
    {"input": [".*prank me"],
     "reply": (["Will do, NN","I would never","Don't give me any ideas"],["<eval>webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')</eval>","<eval>webbrowser.open('http://www.nyan.cat')</eval>"])},

    {"input": [".*spell (.+)"],
     "reply": ["Did you mean <eval>', '.join(spellchecker.suggest(self.match.group(1)))</eval>?"]},

    # CHECK CONTACT INFO
    {"input": [".*what's my name", ".*whats my name", ".*what my name's"],
     "reply": ["Your name is NN, NN", "I thought you would know your own name, NN",
               "I call you NN, but we all know what people call you behind your back"]},
    {"input": [".*what's my (birthday|bday|b-day|birth day|date of birth|day of birth|birth date)",".*'s i (born|birthed)"],
     "reply": ["You were born on BDAY, NN"]},
    {"input": [".*'s my gender", ".+i (male|female|a boy|a girl|a man|a woman)"],
     "reply": ["You're GENDER, NN", "You should know this, NN"]},

    # CHANGE CONTACT INFO (birth date, nickname, full name, location of living, gender)
    {"input": [".*my name's (.+)", ".*my name to (.+)","(.+)'s my name","(.+)'s my name"],
     "reply": (["OK","Okay then","If you say so"],
               "<exec>if self.toolBox.promptYN('Change your nickname to %s? ' % self.match.group(1)): self.toolBox.changeContact(0,{'NN':self.match.group(1)})</exec>")},
    {"input": [".*my (birthday|bday|b-day|birth day|date of birth|day of birth|birth date)'s (.+)", ".*my (birthday|bday|b-day|birth day|date of birth|day of birth|birth date) to (.+)","(.+)'s my (birthday|bday|b-day|birth day|date of birth|day of birth|birth date)",".*i's (born on|birthed on|born) (.+)"],
     "reply": (["OK","Okay then","If you say so"],
               "<exec>if self.toolBox.promptYN('Change your birth date to %s? ' % self.match.group(2)): self.toolBox.changeContact(0,{'BDAY':parse(self.match.group(2)).strftime('%d/%m/%Y')})</exec>")},
    {"input": [".*i'm (female|male|a boy|a girl|a man|a woman)",".*my gender's (female|male|a boy|a girl|a man|a woman)"],
     "reply": (["OK","Okay then","If you say so"],
               "<exec>if self.toolBox.promptYN('Change your gender to %s? ' % self.match.group(1)): self.toolBox.changeContact(0,{'GENDER':self.match.group(1)})</exec>")},


    # FAVORITE STUFF (to be added)
    {"input": [".*your favorite (.+)"],
     "reply": ['I have no favorite <eval>self.match.group(1)</eval>',"I don't like to play favorites, NN"]},

    # HELP
    {"input": [".*help",".*(should|can|) i (should |can |)ask you"],
     "reply": ["You can ask me to search the internet for stuff, tell you the weather, get the time and date, open files, make random numbers, and all sorts of stuff. I suggest you just start talking."]},


    # RANDOM DECISIONS
    {"input": [".*number between (\d+) and (\d+)",".*pick a number from (\d+) to (\d+)"],
     "reply": (["it's ","that would be "],"<eval>str(random.randint(int(self.match.group(1)),int(self.match.group(2))))</eval>")},
    {"input": [".*flip a coin"],
     "reply": (["it landed on ","it landed "],"<eval>'heads' if random.randint(0,1)==1 else 'tails'</eval>",[" this time",""])},
    {"input": ["roll a (\d+) sided die","roll a (\d+)-sided die"],
     "reply": (["it's ","rolling... it's ","OK, it's "],"<eval>str(random.randint(1,int(self.match.group(1))))</eval>",[" this time",""])},
    {"input": ["roll a die"],
     "reply": (["it's ","rolling... it's ","OK, it's "],"<eval>str(random.randint(1,6))</eval>",[" this time",""])},

    # TIMER/COUNTDOWN
    {"input": [".*(countdown|count down from (\d+))"],
     "reply": (["all done","happy new years!"],'''<exec>
num = int(self.match.group(2))
for i in range(num):
    print(num-i)
</exec>''')},

    {"input": [".*countdown|count down"],
         "reply": (["all done","happy new years!"],'''<exec>
num = self.toolBox.promptD("from what?")[0]
for i in range(num):
    print(num-i)
    </exec>''')},


    # SEARCHING THE WEB
    # maps
    {"input": [".*directions from (.+) to (.+)",".*directions (.+) to (.+)",".*directions to (.+)"],
     "reply": (["Opening Google Maps...","Finding directions..."],"<eval>webbrowser.open(self.toolBox.directionsURL(*reversed(self.match.groups())))</eval>")},
    {"input": [".*how (many hours|many miles|long) from (.+) to (.+)"],
     "reply": (["Opening Google Maps...","Finding directions..."],"<eval>webbrowser.open(self.toolBox.directionsURL(self.match.group(3),self.match.group(2)))</eval>")},
    {"input": ["where's (.+)","show me (.+) on .*map","find (.+) on .*map","search for (.+) on .*map","search (.+) on .*map"],
     "reply": ("Opening Google Maps...","<eval>webbrowser.open(self.toolBox.locationURL(self.match.group(1)))</eval>")},

    # open website
    {"input": [".*open (.+)\.(.+)"],
     "reply": ("",'''<eval>webbrowser.open("https://%s.%s" % self.match.groups())</eval>''')},
    {"input": [".*open (https|http)://(.+)\.(.+)"],
     "reply": ("",'''<eval>webbrowser.open("%s://%s.%s" % self.match.groups())</eval>''')},

    # search google
    {"input": [''.join(i) for i in list(itertools.product([".*find ",".*search the .*web.* for ",".*search for ",".*search ",".*browse",".*show me "],
                                                         ["(.+) images","(.+) photos","(.+) pictures","(.+) pics","pictures of (.+)","pics of (.+)","images of (.+)","photos of (.+)"]))],
     "reply": ["<eval>webbrowser.open('https://www.google.com/search?q=%s&tbm=isch' % self.match.group(1))</eval>"]},
    {"input": [''.join(i) for i in list(itertools.product([".*find ",".*search for ",".*search ",".*browse",".*show me "],
                                                         ["(.+) videos","(.+) vids","videos of (.+)","vids of (.+)"]))],
     "reply": ["<eval>webbrowser.open('https://www.google.com/search?q=%s&tbm=vid' % self.match.group(1))</eval>"]},
    {"input": ["google (.+)","look up (.+)","search .*for (.+)"],
     "reply": ["<eval>self.toolBox.googleIt(self.match.group(1))</eval>"]},

    # wikipedia
    {"input": [".*wikipedia for (.+)",".*wikipedia (.+)"],
     "reply": ["<eval>self.toolBox.wikiLookup(self.match.group(1)) if self.toolBox.wikiLookup(self.match.group(1)) is not None else 'No Wikipedia article found'</eval>"]},
    {"input": ["who's (.+)","who're (.+)"],
     "reply": ["<eval>self.toolBox.personLookup(self.match.group(1))</eval>"]},

    # news
    {"input": [".*news about (.+)",".*news for (.+)"],
     "reply": (["Will do, NN","opening Google News...","Here's the news about <eval>self.match.group(1)</eval>"],"<eval>webbrowser.open('https://news.google.com/news/search/section/q/%s' % self.match.group(1))</eval>")},
    {"input": [".*news"],
     "reply": (["Will do, NN","opening Google News...","Here's the news"],"<eval>webbrowser.open('https://news.google.com/news/')</eval>")},

    # dictionary stuff
    {"input": ["define (.+)",".+definition of (.+)",".+meaning of (.+)",".+ does (.+) mean"],
     "reply": ("<eval>self.match.group(1)</eval>: ","<eval>self.toolBox.define(re.sub(r'[\W]', ' ', self.match.group(1)),0)</eval>")},
    {"input": [".*example of (.+) .*in a sentence",".*use (.+) in a sentence"],
     "reply": ("example sentence for <eval>self.match.group(1)</eval>: ","<eval>random.choice(self.toolBox.usedInASentence(re.sub(r'[\W]', ' ', self.match.group(1))))</eval>")},
    {"input": [".*synonyms for (.+)",".*synonyms of (.+)",".*synonym for (.+)",".*synonym of (.+)",".*another word for (.+)",".*other word for (.+)",".*other words for (.+)"],
     "reply": (["Here's some synonyms for <eval>self.match.group(1)</eval>: ","Other words for <eval>self.match.group(1)</eval>: "],"<eval>self.toolBox.thesaurus(self.match.group(1))</eval>")},

    # weather
    {"input": [".*weather","how's it outside","what's it like outside"],
     "reply": ["<eval>'location: {}\\ndescription: {}\\ntemperature: {}°F\\nhumidity: {}%\\natmospheric pressure: {}'.format(*self.toolBox.weather(['name'],['weather',0,'description'],['main','temp'],['main','humidity'],['main','pressure']))</eval>"]},
    {"input": [".*humidity", "is it humid", ".+humid .*today", ".+humid out"],
     "reply": (["right now, ", ""], "the humidity is ", "<eval>str(self.toolBox.weather(['main','humidity'])[0])</eval>", " percent",[", NN", ""])},
    {"input": [".*temperature"]+list(itertools.chain.from_iterable([".+%s .*today" % s,".+%s out" % s] for s in syn('hot')))+list(itertools.chain.from_iterable([".+%s .*today" % s,".+%s out" % s] for s in syn('cold'))),
     "reply": (["the temperature is "],"<eval>str(self.toolBox.weather(['main','temp'])[0])</eval>",[" degrees","°F"],[", NN",""])},
    {"input": [".*wind pressure",".*atmospheric pressure",".*air pressure"],
     "reply": (["the atmospheric pressure is ","the air pressure is "],"<eval>str(self.toolBox.weather(['main','pressure'])[0])</eval>",[", NN",""])},
    {"input": [".*wind"],
     "reply": (["the wind speed is ","the wind is speeding around at "],"<eval>str(self.toolBox.weather(['wind','speed'])[0])</eval>",[" miles per hour"," mph"],[", NN",""])},

    # time/date
    {"input": [".+time's it",".+s the time",".*current time"],
     "reply": (["It's ","the clock says "],"<eval>time.asctime().split()[3]</eval>",[" o'clock",""],", NN")},
    {"input": [".+s the date",".*current date",".+today's date",".+day's it",".*what's today"],
     "reply": ("It's ","<eval>' '.join(time.asctime().split()[:3])</eval>",", NN")},
    {"input": [".+year's it",".+'s the year",".+century's it",".*current year",".*current century"],
     "reply": (["It's ","The year is ","It's the year of "],"<eval>time.asctime().split()[4]</eval>",", NN")},

    # LOCATION
    {"input": ["where.+am i","where.*'re we","where's here",".*my location"],
     "reply": (["you're in ","your location is "],"<eval>'{}, {}'.format(*self.toolBox.locationData('city','region_code'))</eval>",[", NN",""])},
    {"input": [".*zipcode"],
     "reply": (["your zipcode is "],"<eval>'{}'.format(*self.toolBox.locationData('zip_code'))</eval>")},
    {"input": [".+state am i in",".+region am i in",".+state i am in",".+region i am in",".+my state",".+my region"],
     "reply": (["right now, ",""],["you're in "],"<eval>self.toolBox.locationData('region_name')[0]</eval>",[", NN",""])},
    {"input": [".+city am i in",".+city i am in",".+city that i am in",".+my city"],
     "reply": (["right now, ",""],["you're in ","your city is "],"<eval>self.toolBox.locationData('city')[0]</eval>",[", NN",""])},
    {"input": [".+country am i in",".+country i am in",".+country that i am in",".+my country"],
     "reply": (["right now, ",""],["you're in ","your country is ","you're standing in the country of "],"<eval>self.toolBox.locationData('country_name')[0]</eval>",[", NN",""])},
    {"input": [".*time zone",".*timezone"],
     "reply": (["right now, ",""],["you're in the "],"<eval>self.toolBox.locationData('time_zone')[0]</eval>"," timezone")},
    {"input": [".*longitude",".*latitude",".*coordinates"],
     "reply": (["right now, ",""],["you're at latitude/longitude "],"<eval>'{}, {}'.format(*self.toolBox.locationData('latitude','longitude'))</eval>")},
    {"input": [".*my ip",".*ip address"],
     "reply": ("your ip is ","<eval>self.toolBox.locationData('ip')[0]</eval>",[", NN",""])},

    # OPEN FILE
    {"input": [".*open (.+)"],
     "reply": ['''<exec>if self.toolBox.promptYN('Open file %s? ' % self.match.group(1)):
    try: os.startfile(self.match.group(1))
    except: print('Unable to open file')</exec>''']},

    # JUST IN CASE

    {"input": [".*why not"],
     "reply": ["because I said so"]},
    {"input": [".*why"],
     "reply": ["because I said so"]},

    {"input": [".*i don't",".*i do not"],
     "reply": ["I know you don't", "you should"]},
    {"input": [".*i do"],
     "reply": ["I don't","no you don't","you do?"]},

    {"input": ["really"],
     "reply": ["yes, really","nope"]},

    {"input": ["don't ask\Z"],
     "reply": ["don't ask what?"]},

    {"input": [".*he's (.+)"],
     "reply": ["who's <eval>self.match.group(1)</eval>?","how <eval>self.match.group(1)</eval>","very <eval>self.match.group(1)</eval>"]},
    {"input": [".*it's (.+)"],
     "reply": ["what's <eval>self.match.group(1)</eval>?","very <eval>self.match.group(1)</eval>","that's <eval>self.match.group(1)</eval>"]},
    {"input": [".*that's (.+)"],
     "reply": ["it is <eval>self.match.group(1)</eval>","'tis very <eval>self.match.group(1)</eval>"]},

    {"input": [".*are you (.+)"],
     "reply": ["I am <eval>self.match.group(1)</eval>","I am not <eval>self.match.group(1)</eval>"]},

    {"input": [".*what do you (.+)"],
     "reply": (["you know what I <eval>self.match.group(1)</eval>"],[", NN",""])},
    {"input": [".*who do you (.+)"],
     "reply": (["you should know who I <eval>self.match.group(1)</eval>","I <eval>self.match.group(1)</eval> everyone"],[", NN",""])},
    {"input": [".*when do you (.+)"],
     "reply": (["I <eval>self.match.group(1)</eval> whenever I want","I <eval>self.match.group(1)</eval> all day","I never <eval>self.match.group(1)</eval>"],[", NN",""])},
    {"input": [".*where do you (.+)"],
     "reply": (["I <eval>self.match.group(1)</eval> all over the place","I <eval>self.match.group(1)</eval> where ever you want"],[", NN",""])},

    {"input": ["i'm not (.+)"],
     "reply": (["You aren't <eval>self.match.group(1)</eval>","You are <eval>self.match.group(1)</eval>","if you say so"],[", NN",""])},

    {"input": ["okay","ok"],
     "reply": ["OK","okie dokie"]},

    {"input": ["i'm sorry","sorry"],
     "reply": ["Don't be sorry, NN","You better be sorry!"]},

    {"input": ["what?!+","huh"],
     "reply": ["what?","huh?"]},

    {"input": ["yes\!"],
     "reply": ["no!"]},
    {"input": ["no\!"],
     "reply": ["yes!"]},
    {"input": ["yes\?"],
     "reply": ["no?"]},
    {"input": ["no\?"],
     "reply": ["yes?"]},
    {"input": ["yes"],
     "reply": ["no"]},
    {"input": ["no"],
     "reply": ["yes"]},

    # Should I search the web for...

    {"input": [".*((how|where|when|what)( to| do|'s|'re) .+)",".*(why( do|'re|'s) .+)"],
     "reply": (["Ok then","If you say so"],'''<exec>tmp=self.match.group(1)
if self.toolBox.promptYN(random.choice(['Should I search the web for %s? ' % tmp,'Do web search for %s? ' % tmp])):
    webbrowser.open('https://www.google.com/search?q=%s' % tmp)</exec>''')},

]