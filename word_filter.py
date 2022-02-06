import itertools
import json
import os
import string
import re
import sys

from thefuzz.StringMatcher import StringMatcher as SequenceMatcher

from clogs import logger

import config

# define functions on import based on config, then create one final function to be exposed

master_replace_dict = {}

if config.blocked_words_clean_confusables:
    with open("confusables.json", "r", encoding="utf8") as f:
        confusables = json.load(f)

    # ascii letters
    for key in list(confusables.keys()):
        if key in string.ascii_letters:
            del confusables[key]

    master_replace_dict = {**master_replace_dict, **confusables}

if config.blocked_words_clean_leet:
    leet = {
        "0": "o",
        "1": "l",
        "2": "r",
        "3": "e",
        "4": "a",
        "5": "s",
        "6": "g",
        "7": "t",
        "8": "b",
        "9": "p"
    }
    master_replace_dict = {**master_replace_dict, **leet}

if config.blocked_words_clean_whitespace:
    # for some godforsaken reason, the best way to find all whitespace is to iterate over every unicode character and
    # regex it. there is no constant. fucking why?
    s = re.compile(r"^\s$", re.UNICODE)
    for c in range(sys.maxunicode + 1):
        u = chr(c)
        if s.match(u):
            master_replace_dict[u] = ""

if config.blocked_words_clean_to_letters:
    def clean1(letter):
        letter = master_replace_dict.get(letter, letter)
        return letter if letter in string.ascii_letters + " " else ""
else:
    def clean1(letter):
        return master_replace_dict.get(letter, letter)

if config.blocked_words_disregard_dictionary_words:
    from hunspell import Hunspell
    h = Hunspell("en_US", hunspell_data_dir=os.path.join(os.path.dirname(os.path.realpath(__file__)), "dictionaries"))
    for word in config.blocked_words:
        h.remove(word)


def clean(confused_string: str) -> str:
    cleaned = ("".join(list(map(clean1, confused_string)))).lower()
    if config.blocked_words_clean_repeated_characters:
        return re.sub(r'(.)\1+', r'\1\1', cleaned)
    else:
        return cleaned


def partial_ratio(longer, shorter):
    # adapted from thefuzz to work better for my needs

    m = SequenceMatcher(None, shorter, longer)
    blocks = m.get_matching_blocks()
    topscore = 0
    topmatch = ""
    for block in blocks:
        long_start = block[1] - block[0] if (block[1] - block[0]) > 0 else 0
        long_end = long_start + len(shorter)
        long_substr = longer[long_start:long_end]

        m2 = SequenceMatcher(None, shorter, long_substr)
        r = m2.ratio()
        if r > topscore:
            topscore = r
            topmatch = long_substr

    return int(round(100 * topscore)), topmatch


if config.blocked_words_fuzzy_tolerance >= 100:
    def match1(haystack: str, needle: str) -> bool:
        return clean(needle) in clean(haystack)
else:
    def match1(haystack: str, needle: str) -> bool:
        confidence, match = partial_ratio(clean(haystack), clean(needle))
        if confidence == 100:
            return True
        if confidence >= config.blocked_words_fuzzy_tolerance:
            # if config set and match found in dictionary, return false. otherwise, count the match!
            if not (config.blocked_words_disregard_dictionary_words and h.spell(match.strip())):
                logger.debug(f"`{match}` within `{haystack}` matches `{needle}` by {confidence}%")
                return True
            else:
                return False


def contains_blocked_word(candidate: str) -> bool:
    # yes, any() would be cleaner, but might take more time cause it wont return early
    for word in config.blocked_words:
        if match1(candidate, word):
            return True
    return False
