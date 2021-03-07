#!/usr/bin/python

# This file will parse a given string,
# And find/act on keywords

import random
import pkgutil
import inspect
import traceback
import string
import re
import logging

from chaslib.soundtools import *
from chaslib.netools import *
from chaslib.misctools import get_logger


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

            if sent[i:i+1] == first_char:

                # If first chars match

                if sent[i:len_state+i] == state:

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

            for j in range(i+1, len(sent)):

                curr_val_two = sent[j]

                if curr_val_two == ' ':

                    # Found a word! Appending to word list!

                    words.append(sent[i+1:j])

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

        return sent[index+4:], talk

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


class BasePersonality(object):

    """
    CHAS BasePersonality Parent Class
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
        """

        pass

    def unload(self):

        """
        Method called when the extension is removed from our cache.
        This is the final method that will be called before the function is removed via garbage collection.

        The function should finish up everything that the personality is doing.
        'stop()' will always be called before this function is called.
        """

        pass

    def start(self):

        """
        Method called when personality is selected
        Should be overridden in child class
        """

        pass

    def stop(self):

        """
        Method called when personality is de-selected
        Should be overridden in child class
        """

        pass

    def handel(self, mesg, talk, win):

        """
        Method for handling input to personality
        Should be overridden in child class
        :param mesg: Message as string
        :param talk: Boolean determining if we are talking
        :param win: Output object, differs based on talk value
        """

        pass

    def _bind_chas(self, chas):

        """
        Binds CHAS to the personality
        :param chas: CHAS Masterclass
        """

        self.chas = chas


class Personalities:

    """
    CHAS BasePersonality manager
    """

    def __init__(self, chas):

        self.chas = chas  # CHAS Masterclass instance
        self.selected = None  # Selected personality
        self._person = []  # List of personalities
        self._name = 'BasePersonality'  # Name of personality parent class
        self._core = CORE()  # CHAS CORE personality

        self.log = get_logger("CORE:PERSON_HAND")

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
        """

        self.log.info("Parsing and rebuilding personality cache...")

        # Clearing personality list

        self.stop()

        # Adding CORE personality to list

        self.load_personality(self._core)

        # Automatically select the CORE personality

        self.select(self._core.name)

        # Getting personalities from directory

        final = []
        val = self._parse_directory([self.chas.settings.personality_dir], final)

        if not val:

            # Failed to parse extensions

            return False

        # Starting personalities

        for per in final:

            # Attempt to load personality:

            self.load_personality(per)

        return True

    def select(self, name):

        """
        Selects personality to be used by name.
        We stop the currently selected personality,
        and start the incoming personality.

        If the 'start()' method fails,
        then we fall back on 'CORE:PERSONALITY'
        to act as a placeholder and stable solution.

        We return True for success, and False for failure.

        :param name: Name of personality
        :type name: str
        :return: True for success, False for Failure
        :rtype: bool
        """

        self.log.info("Selecting personality: [{}]...".format(name))

        # Attempt to find personality:

        person = self.find(name)

        if not person:

            # Unable to find personality

            self.log.warning("Unable to select personality: [{}] - Name not found!".format(name))

            return False

        # Stopping current personality, if one is selected:

        if self.selected is not None:

            self.stop_personality(self.selected.name)

            # Deselecting current personality

            self.log.debug("De-selecting current personality: [{}]...".format(self.selected.name))

            self.selected._deselect()
            self.selected = None

        # Stating new personality:

        val = self.start_personality(name)

        # Check if starting was successful:

        if not val:

            # Failed to start, fallback

            self.log.warning("Failed to start [{}] - Falling back on CORE:PERSONALITY".format(name))

            return False

        # Changing selected personality

        self.log.debug("Setting selected to: {}".format(person.name))

        self.selected = person

        # Setting selected value:

        self.selected._select()

        # BasePersonality successfully selected!

        self.log.info("Successfully selected personality: [{}]!".format(name))

        return True

    def load_personality(self, person):

        """
        Loads a given personality, and adds it to the collection.

        The personality MUST inherit 'BasePersonality',
        or else the operation will fail.

        We also call 'load()' for the personality to be added.
        If this method fails, then we will fail and refuse to add it.

        :param person: Personality to add
        :type person: BasePersonality
        :return: True for success, False for failure
        :rtype: bool
        """

        # Checking if personality is valid subclass:

        if not isinstance(person, BasePersonality):

            # Not a valid personality!

            self.log.warning("Object [{}] is not a valid personalty! Must subclass BasePersonality!")

            return False

        self.log.debug("Loading personality: [{}]...".format(person.name))

        # Add the CHAS instance to it:

        person.chas = self.chas

        # Load the personality:

        try:

            person.load()

        except Exception as e:

            # Failed to load personality, skip the operation:

            self.log.warning("Failed to load personality: [{}] - Exception upon 'load()'!".format(person.name),
                             exc_info=e)

            return False

        # Add the personality to the list:

        self._person.append(person)

        self.log.debug("Successfully loaded personality: [{}]!".format(person.name))

        return True

    def start_personality(self, name):

        """
        Starts a personality.

        We do this by calling the 'start()' function of the personality.

        You normally shouldn't call this method,
        as it is already invoked by 'select()'.

        However, it is provided for logging capabilities,
        and if you have a special use for this feature.

        We return True if successful, False if not.

        :param name: Name of the personality to start
        :type name: str
        :return: True for success, False for failure
        :rtype: bool
        """

        self.log.debug("Starting personality with name: [{}]...".format(name))

        # Get the personality by name:

        per = self.find(name)

        if not per:

            # Unable to find personality

            self.log.warning("Unable to start personality: [{}] - Name not found!!".format(name))

            return

        # Attempting to start the personality:

        try:

            per.start()

        except Exception as e:

            # Something went wrong while starting personality
            # Logging and returning failure

            self.log.warning("Exception occurred when starting: [{}]".format(self.selected.name), exc_info=e)

            return False

        # Started personality!

        self.log.debug("Successfully started personality: [{}]!".format(name))

        return True

    def stop_personality(self, name):

        """
        Stops a personality.

        We do this by calling the 'stop()' function of the personality.

        You normally shouldn't call this method,
        as it is already invoked by 'select()'.

        However, it is provided for logging capabilities,
        and if you have a special use for this feature.

        We return True if successful, False if not.

        :param name: Name of the personality to stop
        :type name: str
        :return: True for success, False for failure
        :rtype: bool
        """

        self.log.debug("Stopping personality with name: [{}]".format(name))

        # Attempt to find the personality

        person = self.find(name)

        if not person:

            # Unable to find personality

            self.log.warning("Unable to stop personality: [{}] - Name not found!".format(person))

        try:

            # Try to stop the personality:

            self.selected.stop()

        except Exception as e:

            # Something went wrong while stopping personality
            # Logging and continuing

            self.log.warning("Exception occurred when stopping: {}".format(self.selected.name), exc_info=e)

            return False

        # BasePersonality stopped successfully!

        self.log.debug("Successfully stopped personality: [{}]!".format(name))

        return True

    def unload_personality(self, name):

        """
        Unloads a personality by name.
        This not only stops the personality,
        removes it from the personality cache.

        We call 'unload()' to tell the personality to finish up whatever it is doing.
        Even if 'unload()' fails, we log the failure and remove it anyway.

        To work with unloaded personalities,
        re-build the personality cache with 'parse_personalities'.

        :param name: Name of the personality to unload
        :type name: str
        """

        self.log.debug("Un-loading personality with name: {}".format(name))

        # Finding personality:

        person = self.find(name)

        if person is None:

            # Could not find, return

            self.log.warning("Could not unload personality with name: [{}]!".format(name))

            return

        # Stopping the personality:

        self.stop_personality(name)

        # Un-load the personality:

        try:

            person.unload()

        except Exception as e:

            # Failed to unload personality, log it and continue

            self.log.warning("Exception occurred when unloading personality: [{}]".format(name), exc_info=e)
            self.log.warning("We will skip calling 'unload()' and will forcefully remove [{}]".format(name))

        # Remove the personality from the personality cache:

        self.log.debug("Removing [{}] from personality cache...".format(name))

        self._person.remove(person)

        self.log.debug("Unloaded personality [{}] from cache!".format(name))

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

            traceback.print_exc()

            return False

        return True

    def stop(self):

        """
        Stops and unloads all personalities.
        """

        self.log.debug("Stopping and unloading all personalities...")

        for num, per in enumerate(self._person):

            # Unload the personality:

            self.unload_personality(per.name)

        self.log.debug("Done stopping and unloading all personalities!")

    def find(self, name):

        """
        Finds and returns a personality by name.
        We return 'None' if the extension is not found.

        :param name: Name of personality to remove
        :type name: str
        :return: Personality with name
        :rtype: BasePersonality
        """

        # Iterate over all personalities"

        self.log.debug("Searching for personality with name: [{}]...".format(name))

        for per in self._person:

            # Check if the name matches:

            if per.name == name:

                # Found our personality! Return it...

                self.log.debug("Found personality [{}]!".format(name))

                return per

        # Unable to find our personality...

        self.log.warning("Unable to find personality [{}]!".format(name))

        return None

    def handel(self, mesg, talk, win):

        """
        Handles input from user.

        :param mesg: Input
        :param talk: Weather we are talking
        :param win: Output object, varies based on talk
        """

        self.log.debug("Sending text [{}] to personality [{}]".format(mesg, self.selected.name))

        self.selected.handel(mesg, talk, win)

        return


class CORE(BasePersonality):

    """
    CHAS CORE personality
    Offers very little functionality, acts as a dummy personality,
    until different one can be loaded
    """

    def __init__(self):

        super(CORE, self).__init__('CORE', 'CHAS Core BasePersonality')
        self.last = None  # Last entered input
        self.out = "CORE:PERSONALITY"  # Output value
        self.chas = None  # CHAS Instance

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

            win.add("Why do you repeat yourself?", prefix=self.out)

            return

        self.last = mesg

        if keyword_find(mesg, 'hello'):

            win.add("Hello Human.", prefix=self.out)

            return

        if keyword_find(mesg, 'goodbye'):

            win.add("Farewell Human.", prefix=self.out)

            return

        if keyword_find(mesg, ['thank', 'thanks']):

            win.add("I live to please.", prefix=self.out)

            return

        if keyword_find(mesg, 'say'):

            # Send message to the voice synth

            text = mesg[mesg.index("say") + 4:]
            self.chas.speak.speak(text)

            return

        else:

            win.add("I don't understand.", prefix=self.out)
