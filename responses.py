import random
import itertools
import time
import re
import json

import requests
import yaml

from bs4 import BeautifulSoup

session = requests.session()

def custom_scanner(context):
    internal_scanner = json.scanner.py_make_scanner(context)

    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    def _scan_once(string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx) from None
        if nextchar == '"':
            return parse_string(string, idx + 1, strict)
        elif nextchar == '{':
            return parse_object((string, idx + 1), strict,
                _scan_once, object_hook, object_pairs_hook, memo)
        elif nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        elif nextchar == 'u' and string[idx:idx + 9] == 'undefined':
            return None, idx + 9
        return internal_scanner(string, idx)

    def scan_once(string, idx):
        try:
            return _scan_once(string, idx)
        finally:
            memo.clear()

    return scan_once

class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # override scanner
        self.scan_once = custom_scanner(self)


def offlineTest(url='https://www.github.com/', timeout=None):
    try:
        requests.get(url, timeout=timeout)
        return False
    except requests.ConnectionError:
        return True


offlineMode = offlineTest()


def syn(word,amount=10,return_original=True):
    if offlineMode is False:
        url = "http://www.thesaurus.com/browse/{}".format(word)
        page = session.get(url,headers={"user-agent": "Mozilla/5.0"})  # session.get() is faster than requests.get()
        initial_state = re.search(r'<script>window\.INITIAL_STATE = (.+);</script>', page.text)
        try:
            j = json.loads(initial_state.group(1), cls=CustomJSONDecoder)
        except json.decoder.JSONDecodeError:
            #~ print(f"Error decoding '{initial_state.group(1)}'")
            raise
        posTabs = j['searchData']['tunaApiData']['posTabs']
        syns = [s['term'] for s in posTabs[0]['synonyms']]
        if syns:
            syns = syns if amount is None else syns[:amount]
            if return_original:
                syns.append(word)
            return syns
    return [word]


def regex_syn(word,amount=10):
    if offlineMode is False:
        return '|'.join(syn(word,amount))
    else:
        return word


floatRegex = r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|[0-9]*\.[0-9]+)(?:[Ee]\+[0-9]+)?"

mathBeforeFloat = r"(?:(?:the )?(?:sqrt|square root|cube root|cosine|cos|sine|sin|tangent|tan)(?: of)?\s)*"
mathOps = r"\+|plus|\*|times|multiplied by|\-|minus|\/|divided by|over|\*\*|\^|to the power of"
mathAfterFloat = r"(?:(?:\ssquared|\scubed)?(?:\s?(?:{})\s?{}{})?)+".format(mathOps, mathBeforeFloat, floatRegex)

mathFullNomial = (mathBeforeFloat + floatRegex + mathAfterFloat)

mathBetweenNomials = r" and "
mathBeforeNomialOp = "(?:the )?(?:sum|quotient|difference|difference between)(?: of)? "

mathFull = "(?:{}|{})".format(mathBeforeNomialOp + mathFullNomial + mathBetweenNomials + mathFullNomial, mathFullNomial)

# GUIDE TO EDITING:

# FOR REPLY:
# ("something"," does"," something") to concatenate (output is "something does something")
# ["something","something else","another thing"] to randomly choose or for replies accept any
# e.g. (["that ","this "],["cat ","dog ","guy "],[["eats","enjoys","attacks"],["ate","enjoyed","attacked"]]," children")

# FOR INPUT:
# ["hi","hello","howdy"] checks if any of the strings match the input
# ["hi|hello|howdy","what's up"] - you can also use regex in the strings (https://docs.python.org/3/library/re.html)

# All inputs must be lowercase to work.

with open('responses.yaml') as f:
    RESPONSES = yaml.load(f, Loader=yaml.BaseLoader)
