#!/usr/bin/python

# This file will parse a given string,
# And find/act on keywords

import random
import pkgutil
import inspect
import traceback
import string
import re
from chaslib.soundtools import *
from chaslib.netools import *


def keyword_find(sent, word, start=0):
    # This function takes a string(sent),
    # a searchable phrase(word),
    # a string search starting point,
    # And returns True if present, false if not.
    # Can be passed single string for single response,
    # Or a list for multiple!

    sent = string_clean(sent)

    words = get_words(sent, start)

    # If word var is string:

    if isinstance(word, (str,)):

        word = word.lower()

        # Checking if keyword is present:

        if word in words:

            # Found our lucky keyword!

            return True

        else:

            # Did not find keyword. Better luck next time!

            return False

    # If word var is list:

    if isinstance(word, (list,)):

        # Formatting keywords and checking if they are present:

        for i in range(len(word)):

            if word[i].lower() in words:
                # Found one of our lucky keywords!

                return True

        # Did not find ANY keywords!

        return False


def key_sta_find(sent, state, start=0):
    # Function for finding statement
    # See 'keyword_find' for argument details,
    # As these are the same.

    sent = string_clean(sent)

    # Statement is string

    if isinstance(state, (str,)):

        state = state.lower()

        first_char = state[0:1]
        len_state = len(state)

        # Checking every char to see if their is a match:

        for i in range(start, len(sent)):

            if sent[i:i + 1] == first_char:

                # If first chars match

                if sent[i:len_state + i] == state:

                    # Found key statement!

                    return True

                else:

                    # Rest don't match, DARN!

                    continue

        # Did not find key statement!

        return False

    # Statement is list:

    if isinstance(state, (list,)):

        for j in range(len(state)):

            state_temp = state[j].lower()
            len_state_temp = len(state_temp)
            first_char = state_temp[0:1]

            # Checking every char to see if their is a match:

            for i in range(start, len(sent)):

                if sent[i:i + 1] == first_char:

                    # If first chars match

                    if sent[i:len_state_temp + i] == state_temp:

                        # Found key statement!

                        return True

                    else:

                        # Rest don't match, DARN!

                        continue

        # Didn't find key statement! DARN!

        return False


def get_words(sent, start):
    # Function for generating list of words from string

    words = []

    # Looping through list until we hit a whitespace:

    for i in range(start, len(sent)):

        # Getting current value:

        curr_val = sent[i]

        if curr_val == ' ':

            # If whitespace, find end of word!

            for j in range(i + 1, len(sent)):

                curr_val_two = sent[j]

                if curr_val_two == ' ':
                    # Found a word! Appending to word list!

                    words.append(sent[i + 1:j])

                    break

    return words


def string_clean(temp):
    # Function for cleaning and preparing string for parsing

    # Making lowercase and removing pesky newline chars

    new_str = temp.lower().lstrip()

    # Removing punctuation

    new_str = re.sub("[{}]".format("".join(string.punctuation)), "", new_str)

    # Adding space in front and behind string

    new_str = ' ' + new_str + ' '

    return new_str


def key_search(sent, talk=False):
    # Function for using keywords to do cool stuff!

    # Will be factored out for RE later

    response = ''

    if isinstance(sent, (bool,)):
        return random_fail()

    # Repeat user phrases
    if keyword_find(sent, 'say'):
        index = sent.find(' say ')

        return sent[index + 4:], talk

    # If user needs extra commands:
    if keyword_find(sent, 'help'):
        return help_text()

    # If user says hello:
    if keyword_find(sent, ['hi', 'hello', 'heya', 'howdy']):
        return 'Hello Human'

    # If input dose not match builtins,
    # Iterate over imported modules.

    for i in settings.extensions:

        val, mesg = i.match(sent, talk)

        if val:
            return mesg

    else:

        return random_fail(talk)


def chat_ban(ver):
    resp = f'''+================================================+
C.H.A.S Text Interface system Ver: {ver}
Welcome to the C.H.A.S Text Interface System!
Please make sure your statements are spelled correctly.
C.H.A.S is not case sensitive, so Go CrAzY!
Type 'help' for more details
'''

    return resp


def help_text():
    resp = """+=======================================================+")
--== C.H.A.S Commands: ==--
'help' to show this menu
'exit' to exit chat
+=======================================================+
"""

    return resp


class Personality(object):
    """
    CHAS Personality Parent Class
    """

    def __init__(self, name, desc):
        self.name = name
        self.description = desc
        self.selected = False

    def _select(self):
        """
        Method called to select the personality
        :return:
        """

        self.selected = True

    def _deselect(self):
        """
        Method called to de-select the personality
        :return:
        """

        self.selected = False

    def load(self):
        """
        Method called when personality is first loaded
        Should be overridden in child class
        :return:
        """

        pass

    def start(self):
        """
        Method called when personality is selected
        Should be overridden in child class
        :return:
        """

        pass

    def stop(self):
        """
        Method called when personality is de-selected
        Should be overridden in child class
        :return:
        """

        pass

    def handel(self, mesg, talk, win):
        """
        Method for handling input to personality
        Should be overridden in child class
        :param mesg: Message as string
        :param talk: Boolean determining if we are talking
        :param win: Output object, differs based on talk value
        :return:
        """

        pass

    def _bind_chas(self, chas):
        """
        Binds CHAS to the personality
        :param chas: CHAS Masterclass
        :return:
        """

        self.chas = chas


class Personalities:
    """
    CHAS Personality manager
    """

    def __init__(self, chas):

        self.chas = chas  # CHAS Masterclass instance
        self.selected = None  # Selected personality
        self._person = []  # List of personalities
        self._name = 'Personality'  # Name of personality parent class
        self._core = CORE()  # CHAS CORE personality

        self._core.chas = self.chas

    def get_personalities(self):

        """
        Gets personalities and returns a list of them
        :return:
        """

        return self._person

    def parse_personalities(self):

        """
        Parses and loads all personalities at personality directory
        Starts the personality
        :return:
        """

        # Clearing personality list

        self._person.clear()

        # Adding CORE personality to list

        self._person.append(self._core)

        # Automatically select the CORE personality

        self.select("CORE")

        # Getting personalises from directory

        val = self._parse_directory([self.chas.settings.personality_dir], self._person)

        if not val:
            # Failed to parse extensions

            return False

        # Starting personalities

        for per in self._person:

            try:

                per.load()

            except:

                # Something went wrong while loading personality
                # Logging and removing from list

                self._person.remove(per)

                continue

        return True

    def select(self, name):

        """
        Selects personality to be used by name
        :param name: Name of personality
        :return:
        """

        for per in self._person:

            if per.name == name:

                # Found our personality

                # Stopping current personality

                if self.selected is not None:

                    try:

                        self.selected.stop()

                    except:

                        # Something went wrong while stopping personality
                        # Logging and continuing

                        pass

                    self.selected._deselect()

                # Changing selected personality

                self.selected = per

                # Setting selected value:

                self.selected._select()

                # Starting personality:

                try:

                    per.start()

                except:

                    # Something went wrong while starting personality
                    # Logging and returning failure

                    self.select("CORE")

                    return False

                return True

        return False

    def _parse_directory(self, direct, final):

        """
        Parses personality directory, adds results to final
        :return:
        """

        try:

            for finder, name, _ in pkgutil.iter_modules(path=direct):

                # Loading module for inspection

                mod = finder.find_module(name).load_module(name)

                for member in dir(mod):

                    # Iterating over builtin attributes

                    obj = getattr(mod, member)

                    # Checking if extension is class

                    if inspect.isclass(obj):

                        # Iterating over each parent

                        for parent in obj.__bases__:

                            # Checking class parent

                            if self._name is parent.__name__:
                                # Found a CHAS personality

                                obj._bind_chas(obj, self.chas)

                                final.append(obj())

        except Exception as e:

            # Something went wrong

            print("Their was an error while parsing personalities: {}".format(e))

            traceback.print_exc()

            return False

        return True

    def handel(self, mesg, talk, win):

        """
        Handles inputfrom user
        :param mesg: Input
        :param talk: Weather we are talking
        :param win: Output object, varies based on talk
        :return:
        """

        self.selected.handel(mesg, talk, win)

        return


class CORE(Personality):
    """
    CHAS CORE personality
    Offers very little functionality, acts as a dummy personality,
    until different one can be loaded
    """

    def __init__(self):

        super(CORE, self).__init__('CORE', 'CHAS Core Personality')
        self.last = None  # Last entered input
        self.out = "CORE:PERSONALITY"  # Output value

    def handel(self, mesg, talk, win):

        """
        Handles input from user
        :param mesg: Input
        :param talk: Weather we are talking
        :param win: Output system, varies on talk
        :return:
        """

        if self.last is not None and self.last == mesg:
            # User is repeating

            win.add("Do not repeat yourself.", output=self.out)

            return

        self.last = mesg

        if keyword_find(mesg, 'hello'):
            win.add("Hello Human.", output=self.out)

            return

        if keyword_find(mesg, 'goodbye'):
            win.add("Farewell Human.", output=self.out)

            return

        if keyword_find(mesg, ['thank', 'thanks']):

            win.add("I live to please.", output=self.out)

            return

        else:

            win.add("I don't understand.", output=self.out)