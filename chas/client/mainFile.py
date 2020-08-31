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

from chaslib.socket_client import SocketClient
from chaslib.extension import Extensions
from settings import Settings
from chaslib.soundtools import Listener, Speaker
from chaslib.chascurses import ChatWindow
from chaslib.resptools import Personalities
import curses
import threading

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
        self.settings = Settings()  # CHAS settings object
        self.person = Personalities(self)
        self.server = None  # CHAS server object
        self.extensions = Extensions(self)  # CHAS Extension manager
        self.socket_client = SocketClient(self, self.settings.host, self.settings.port)  # CHAS socket server
        self._master_win = None  # Master Curses window
        self.listener = Listener(self.settings.wake, self)  # CHAS Listener object
        self.speak = Speaker()  # CHAS Speaker object
        self.thread = None

        self.version = '1.0.0'

    def _init_curses(self):

        """
        Configures curses to be used for chas
        :return:
        """

        curses.noecho(True)
        curses.cbreak(True)

    def start(self):

        """
        Starts all CHAS features
        :return:
        """

        # Setting run value

        self.running = True

        # Parsing and loading extensions

        val = self.extensions.parse_extensions()

        # Starting the socket server

        self.socket_client.start_socket_client()

        # Parsing and loading personalities

        self.person.parse_personalities()

        # Starting listener

        self.start_listen()

    def stop(self):

        """
        Stops all CHAS Features
        :return:
        """

        # Setting run value

        self.running = False

        # Stopping socket server

        self.socket_client.stop_socket_client()

        # Disabling extensions:

        self.extensions.stop()

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

            if val:
                
                # Extension handled response
            
                continue

            # Checking remote for response

            data = self.server.get({"voice": word, "talk": True})

            if data['success']:
                
                # Remote was able to handel our input

                self.speak.speak(data['resp'])

                continue

            # Checking personality for response

            self.person.handel(word, True, self.speak)

    def main(self):

        """
        Main method where curses is started
        :return:
        """

        curses.wrapper(self._main)

    def _main(self, win):

        """
        True main class, for use with the curses wrapper
        :param win: Curses window
        :return:
        """

        self._master_win = win

        self.start()

        text = ChatWindow(self, self._master_win)

        text.run()


if __name__ == "__main__":

    # Execute file as script

    chas = CHAS()

    chas.main()
