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


import curses
import threading

from chaslib.socket_server import SocketServer, SocketClient
from chaslib.device import Devices
from chaslib.extension import Extensions
from settings import Settings
from chaslib.soundtools import Listener, Speaker
from chaslib.sound.base import OutputHandler
from chaslib.sound.out import PyAudioModule
from chaslib.chascurses import ChatWindow
from chaslib.resptools import Personalities
from chaslib.misctools import set_chas, get_logger


# These variables are not to be touched!

ver = "1.0.0"
name = "Owen Cochell"


class CHASBase:

    """
    CHASBase - Common features and functionality for client and server.

    We simply define some common components, 
    and provide some functionality useful for the client and the server.

    The client and server each have very diffrent uses and functionality,
    so we offer a way to determine which one is in use,
    which can be useful for extensions that need to determine what they are working with.
    """

    def __init__(self):

        """
        Constructor of the CHAS instance
        """

        self.running = False  # Value if we are running

        set_chas(self)  # Set our CHAS value

        self.settings = Settings()  # CHAS settings object
        self.person = Personalities(self)  # CHAS personalities manager
        self.extensions = Extensions(self)  # CHAS Extension manager
        self._master_win = None  # Master Curses window
        self.listener = Listener(self.settings.wake, self)  # CHAS Listener object
        self.speak = Speaker()  # CHAS Speaker object
        self.thread = None  # Thread object used
        self.exit = 'exit'  # Exit keyword, for exiting chas
        self.chat = None  # CHAS chat window
        self.log = None  # Logging object
        self.sound = OutputHandler()  # Output handler object

        self.client = False  # Value determining if we are a client

        self.net = None  # Networking system to use - Should be overridden by child class

        self.version = '1.0.0'

    def start(self):

        """
        Starts all CHAS features
        """

        # Setting run value

        self.running = True

        # Getting our logger:

        self.log = get_logger("CORE")
        self.log.info("Starting CHAS components...")

        # Starting audio service:

        self.log.info("Starting audio engine...")

        pyaud = PyAudioModule()
        pyaud.special = True

        self.sound.add_output(pyaud)

        self.sound.start()

        # Parsing and loading extensions

        self.log.info("Starting Extension Service...")

        val = self.extensions.parse_extensions()

        # Loading relevant audio modules to the OutputHandler

        # Starting the socket server

        self.log.info("Starting networking...")

        self.net.start()

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

        self.net.stop()

        # Stopping listening service:



        # Disabling extensions:

        self.log.info("Stopping and disabling extension service...")

        self.extensions.stop()

        # Disabling personalities:

        self.log.info("Stopping and disabling personality service...")

        self.person.stop()

        # Stopping audio service:

        self.log.info("Stopping audio engine...")

        self.sound.stop()

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

            if self.client:

                # Check remote, and see if their is a response

                data = self.server.get({"voice": inp, "talk": False}, 2)

                if data["success"]:
                
                    # Server was able to handel input
            
                    self.chat.add(data['resp'], output="REMOTE")
                
                    continue

            # Send input to personality:

            self.person.handel(inp, False, self.chat)

            continue


class CHASServer(CHASBase):

    """
    CHASServer - Master class for the CHAS Server.

    We are optimized for server use,
    meaning that our networking system is a socket server that is meant to server many clients.
    """

    def __init__(self):

        super().__init__()

        # Define our device handler:

        self.devices = Devices(self)

        # Define our networking:

        self.net = SocketServer(self, self.settings.host, self.settings.port)


class CHASClient(CHASBase):

    """
    CHASClient - Master class for the CHAS Client.

    We are optimized for client use,
    meaning that our networking is a simple client that is designed to communicate with a server.
    """

    def __init__(self):

        """
        Constructor of the CHAS instance
        """

        super().__init__()

        self.client = True

        # Define our server object:

        self.server = None  # CHAS server object

        # Defining our networking component:

        self.net = SocketClient(self, self.settings.host, self.settings.port)  # CHAS socket server


if __name__ == "__main__":

    # Execute file as script

    chas = CHASServer()

    chas.main()
