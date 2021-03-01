#!/usr/bin/python

# ENTech SS
# C.H.A.S Network
# ATTENTION:
# +============================================+
# |This script is for LINUX DEVICES ONLY!!!!   |
# |This script is configured for MY network!   |
# |Using this script will probably not work!   |
# +============================================+

# This is the main file were everything will be executed.

# Importing necessary stuff here:

from chaslib.socket_server import SocketServer
from chaslib.device import Devices
from chaslib.extension import Extensions
from settings import Settings
from chaslib.soundtools import Listener, Speaker
from chaslib.chascurses import ChatWindow
from chaslib.resptools import Personalities

from chaslib.misctools import set_chas, get_logger

import curses
import threading
import logging

# These variables are not to be touched!

ver = "1.0.0"
name = "Owen Cochell"


class CHAS:

    """
    Master class of CHAS
    Binds all other subclasses together,
    And provides a shared memory location for all features to operate in
    """

    def __init__(self):

        """
        Constructor of the CHAS instance
        """

        self.running = False  # Value if we are running

        set_chas(self)  # Set our CHAS value

        self.settings = Settings()  # CHAS settings object
        self.person = Personalities(self)  # CHAS personalities manager
        self.devices = Devices(self)  # CHAS device manager
        self.extensions = Extensions(self)  # CHAS Extension manager
        self.socket_server = SocketServer(self, self.settings.host, self.settings.port)  # CHAS socket server
        self._master_win = None  # Master Curses window
        self.listener = Listener(self.settings.wake, self)  # CHAS Listener object
        self.speak = Speaker()  # CHAS Speaker object
        self.thread = None  # Thread object used
        self.exit = 'exit'  # Exit keyword, for exiting chas
        self.chat = None  # CHAS chat window
        self.log = None  # Logging object

        self.version = '1.0.0'

    def start(self):

        """
        Starts all CHAS features
        :return:
        """

        # Setting run value

        self.running = True

        # Getting our logger:

        self.log = get_logger("CORE")
        self.log.info("Starting CHAS components...")

        # Parsing and loading extensions

        self.log.info("Starting Extension Service...")

        val = self.extensions.parse_extensions()

        # Starting the socket server

        self.log.info("Starting Socketserver and networking...")

        self.socket_server.start_socketserver()

        # Parsing and loading personalities

        self.log.info("Starting personality service...")

        self.person.parse_personalities()

        # Starting listener

        self.log.info("Starting audio recognition and listing service...")

        self.start_listen()

    def stop(self):

        """
        Stops all CHAS Features
        """

        # Setting run value

        self.running = False

        self.log.info("!! Stopping CHAS Components... !!")

        # Stopping socket server

        self.log.info("Stopping socketserver and networking...")

        self.socket_server.stop_socketserver()

        # Stopping listening service:



        # Disabling extensions:

        self.log.info("Stopping and disabling extension service...")

        self.extensions.stop()

        # Disabling personalities:

        self.log.info("Stopping and disabling personality service...")

        self.person.stop()

        # Disabling ChatWindow:

        self.log.info("Stopping CURSES output...")

        self.chat.stop()

    def start_listen(self):

        """
        Starts the listen thread
        """

        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def _listen(self):

        """
        Continuously listens
        """

        while self.running:

            # Waiting for keywords

            val = self.listener.continue_listen()

            # Get words from CHAS

            word = self.listener.listen()

            # Handling output

            val = self.extensions.handel(word, True, self.speak)

            if not val:

                # Extensions unable to handle input, send input to personality

                self.speak.speak("I am unable to process your input at this time")

    def main(self):

        """
        Main method where curses is started
        """

        curses.wrapper(self._main)

    def _main(self, win):

        """
        True main class, for use with the curses wrapper
        :param win: Curses window
        """

        self._master_win = win

        max_y, max_x = self._master_win.getmaxyx()

        self.chat = ChatWindow.create_subwin_at_pos(self._master_win, max_y, max_x)

        # Adding CHAS object so the chatwindow can get statistics

        self.chat.chas = self

        # Start the components:

        self.start()

        # Event loop for processing input:

        while True:

            # Get input from text window:

            inp = self.chat.input()

            # Checking for exit keyword:

            if inp == self.exit:

                # Close down CHAS and exit

                self.stop()

                self.log.info("CHAS Shutdown Complete!")

                return

            # Check CHAS extensions:

            if self.extensions.handel(inp, False, self.chat):

                # Extension handled input, continue:

                continue

            # Send input to personality:

            self.person.handel(inp, False, self.chat)

            continue


if __name__ == "__main__":

    # Execute file as script

    chas = CHAS()

    chas.main()
