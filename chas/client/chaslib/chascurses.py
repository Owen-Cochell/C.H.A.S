import curses
import curses.panel
import inspect
from math import ceil, floor

"""
CHAS Curses wrappings.
Includes special curses operations,
As well as custom curses windows to use
"""


class CHASWindow:

    """
    Custom CHAS Window
    """

    def __init__(self, win):

        self.win = curses.newwin()  # Curses window to do our operations on
        self.color = False  # Value determining if we have color
        self._calls = {}  # List of callbacks to be called given a keypress
        self._fallback = {}  # Fallback input handler, when no callbacks for key are found
        #TODO: Add all curses keymaps
        self.keys = {"arrow_up": curses.KEY_UP,
                     "arrow_right": curses.KEY_RIGHT,
                     "arrow_left": curses.KEY_RIGHT,
                     "arrow_down": curses.KEY_DOWN}

        self._init_screen()

    def _init_screen(self):

        """
        Function for setting parameters,
        And preparing the window to be written to
        :return:
        """

        # Turning off the echoing of keys

        curses.noecho()

        # Enabling cbreak mode, disables buffered input

        curses.cbreak(True)

        # Start Keypad handling:

        self.win.keypad(True)

        # Making getch() non-blocking

        self.win.nodelay(True)

        # Allowing scrolling

        self.win.scrollok(True)

        # Allow hardware line editing facilities

        self.win.idlok(True)

        # Checking for color capacities

        if curses.has_colors():

            # Terminal has colors, enabling

            curses.start_color()
            self.color = True

    def add_callback(self, key, call, args=None):

        """
        Adds callback to be called when specified key is pressed
        :param key: Key to be pressed, can be string or list, special characters included
        :param call: Function to be called
        :param args: Args to be passed to the function
        :return:
        """

        # Convert key to string

        key = str(key)

        # Add key/function/args to dictionary of keys to handel

        self._calls[key] = {'call': call, 'args': args}

        return

    def _handel_key(self, key):

        """
        Handles a specified key
        :param key: Key to be handled
        :return:
        """

        if key in self._calls:

            func = self._calls[key]['call']
            args = self._calls[key]['args']

            # Running callback

            func(*args)

            return True

        return False

    def get_input(self):

        pass


class InputWindow:

    """
    CHAS Input window
    Allows for the input of multiple characters, and scrolling
    Will use the ENTIRE window
    """

    def __init__(self, win):

        self.win = win  # Curses window provided

        self.run = True  # Value determining if we are capturing input

        cords = win.getmaxyx()  # Max length of window

        self.max_x = cords[1]  # Max x length of window
        self.max_y = cords[0]  # Max y length of window

        self.curs_x = 0  # Cursor x position
        self.curs_y = 0  # Cursor y position

        self.scroll = 0  # Number of lines we scrolled down

        self.inp = []  # Input data, each entry is a separate character

        self.prompt_len = 0  # Prompt for input system

        self._init_screen()  # Sets certain window attributes

    def _init_screen(self):

        """
        Enables cursor and other arbitrary things
        :return:
        """

        # Enabling cursor

        curses.curs_set(True)

        self.win.keypad(True)

        self.win.scrollok(True)

        self.win.idlok(True)

    def input(self, prompt=""):

        """
        Starts recording input from user
        :param prompt: Prompt to display
        :param echo: Echo keys
        :return:
        """

        self._reset_object()

        self.prompt_len = len(prompt)

        for i in list(prompt):

            self.inp.append(i)

        self.curs_x = self.prompt_len

        self._render()

        while self.run:

            # Getting key

            key = self._get_input()

            # Interpreting key

            if self._handel_key(key):

                # Key has been handled, render screen and continue

                self._render()

                continue

            # Key has not been handled, is string we can work with

            key = chr(key)

            # Altering internal collection of inputs:

            index = self._calc_pos()

            self.inp.insert(index, key)

            # Render in the data and increment the cursor

            self._increment_cursor()
            self._render()

        return self._combine()

    def _reset_object(self):

        """
        Resets the input system and all internal attributes
        :return:
        """

        self.inp = []  # Clearing internal input
        self.run = True  # Setting rune value to True

        self.curs_x = 0  # Setting cursor x to 0
        self.curs_y = 0  # Setting cursor y to 0

        self.scroll = 0  # Setting scroll to zero

        self.win.erase()  # Clears the window

        self.win.refresh()  # Refreshes window to make changes final

    def _get_input(self):

        """
        Gets input from window
        :return:
        """

        # Getting key

        key = self.win.getch()

        return key

    def _handel_key(self, key):

        """
        Handles key to do text operations
        :param key: ASCII number of key pressed
        :return: return True, if handled, False if not
        """

        # Checking key for move cursor operations

        if key == curses.KEY_RIGHT:

            # User pressed right key:

            self._increment_cursor()

            return True

        if key == curses.KEY_LEFT:

            # User pressed left key

            self._decrement_cursor()

            return True

        if key == curses.KEY_UP:

            # User pressed up key

            self._decrement_cursor_line()

            return True

        if key == curses.KEY_DOWN:

            # User pressed down key

            self._increment_cursor_line()

            return True

        if key == curses.KEY_BACKSPACE or chr(key) == b'\x08' or key == 8:

            # User wants to delete previous character

            # Decrementing cursor

            self._decrement_cursor()

            # Deleting cursor at position

            self._delete()

            return True

        if key == curses.KEY_ENTER or key == 10 or key == 13:

            # User pressed enter, end input

            self.run = False

            return True

        elif key > 255:

            # Some other junk key we don't care about

            return True

        return False

    def _get_lines(self):

        """
        Gets the number of lines the internal input will take up
        :return: Number of lines will be used
        """

        return ceil(len(self.inp) / self.max_x)

    def _calc_pos(self):

        """
        Function for calculating the position of a character in the list,
        Uses cursor position
        :return:
        """

        return ((self.curs_y + self.scroll) * self.max_x) + self.curs_x

    def _increment_cursor(self):

        """
        Increments the cursor, moves to new line if necessary
        """

        if self.curs_x == self.max_x - 1:

            # Move cursor to new line

            if self.curs_y == self.max_y - 1 and self._get_lines() > self.curs_y + self.scroll:

                # Scrolling data down one

                self.scroll = self.scroll + 1
                self.curs_x = 0

            elif self.curs_y != self.max_y - 1:

                self.curs_x = 0
                self.curs_y = self.curs_y + 1

        else:

            # Move cursor forward one

            self.curs_x = self.curs_x + 1

    def _decrement_cursor(self):

        """
        Decrements the cursor, moves up lines if necessary
        :return:
        """

        if self.curs_x == 0:

            # Move cursor down one line

            if self.curs_y == 0:

                # Scroll content upwards

                self.scroll = (self.scroll - 1 if self.scroll > 0 else 0)
                self.curs_x = (self.max_x - 1 if self.scroll > 0 else self.prompt_len - 1)

            else:

                # Move cursor up one line

                self.curs_y = self.curs_y - 1
                self.curs_x = self.max_x - 1

        elif self.curs_y == 0:

            # Make sure we don't go over our prompt

            self.curs_x = (self.curs_x - 1 if self.curs_x > self.prompt_len else self.prompt_len)

        elif self.curs_x != 0:

            # Move cursor back one

            self.curs_x = self.curs_x - 1

    def _decrement_cursor_line(self):

        """
        Decrements the cursor by one line
        :return:
        """

        if self.curs_y == 0 and self.scroll > 0:

            # Scroll upwards:

            self.scroll = self.scroll - 1
            self.curs_x = (self.prompt_len if self.scroll == 0 else self.curs_x)

        elif self.curs_y > 0:

            # Scroll cursor up one

            self.curs_y = self.curs_y - 1
            self.curs_x = (self.prompt_len if self.curs_y == 0 else self.curs_x)

    def _increment_cursor_line(self):

        """
        Increments the cursor by one line
        :return:
        """

        if self.curs_y == self.max_y - 1 and self._get_lines() > self.curs_y + self.scroll:

            # Bottom of the screen, scroll content up by one line

            self.scroll = self.scroll + 1

        elif self.curs_y < self.max_y - 1:

            # Move cursor up by one line

            self.curs_y = self.curs_y + 1

    def _delete(self):

        """
        Deletes a character at the given cursor position
        :return:
        """

        # Removing character from internal input

        if self.curs_x + ((self.curs_y + self.scroll) * self.max_x) < len(self.inp):

            # Position is within range, removing character

            self.inp.pop(self._calc_pos())

            # Deleting character at cursor position:

            self.win.delch(self.curs_y, self.curs_x)

        return

    def _combine(self):

        """
        Returns the combined list of inputs
        :return: String of all combined inputs
        """

        return "".join(self.inp)[self.prompt_len:]

    def _render(self):

        """
        Renders the internal input to screen
        Uses cursor pos, scroll level, and max cords.
        :return:
        """

        # Calculate start index

        start = (self.scroll * self.max_x)
        end = (start + (self.max_y * self.max_x))

        # Getting output from list

        out = self.inp[start:end]

        for ind, char in enumerate(out):

            # Calculating x and y values for current character

            y = floor(ind / self.max_x)
            x = ind - (y * self.max_x)

            # Adding character to window

            self.win.addstr(y, x, char)

        # Checking if we should make the bottom line blank

        if self.scroll + self.max_y == self._get_lines() + 1 and self.curs_y == self.max_y - 1:

            # Deleting chars at bottom line

            out = " " * (self.max_x - 1)

            self.win.addstr(self.max_y - 1, 0, out)

        """
        # Some debug info,
        # TODO: REMOVE THIS SECTION!!!

        self.win.addstr(self.max_y - 1, 0, f"X: {self.curs_x} ; Y: {self.curs_y} ; SCROLL: {self.scroll}")
        """

        # Moving cursor to set position

        self.win.move(self.curs_y, self.curs_x)

        # Refreshing window, so changes are shown

        self.win.refresh()

        return


class Border:

    """
    Widget for creating a boarder around windows, can't be edited
    """

    def __init__(self, win):

        self.win = win  # Master window to use
        self.subwin = None  # Subwindow surrounded by border
        cords = self.win.getmaxyx()

        self.max_y = cords[0]  # Max y cords
        self.max_x = cords[1]  # Max x cords

    def _create(self):

        """
        Creates subwindow inside border
        :return:
        """

        self.subwin = self.win.derwin(self.max_y - 2, self.max_x - 2, 1, 1)

    def border(self, ls=0, rs=0, ts=0, bs=0, tl=0, tr=0, bl=0, br=0):

        """
        Generates the boarder and returns the subwindow for writing
        :param ls: Left Side
        :param rs: Right Side
        :param ts: Top
        :param bs: Bottom
        :param tl: Upper left cornet
        :param tr: Upper right corner
        :param bl: Bottom left corner
        :param br: Bottom right corner
        :return:
        """

        # Rendering border

        self.win.border(ls, rs, ts, bs, tl, tr, bl, br)

        self.win.refresh()

        # Creating subwindow

        self._create()

        # Retuning subwindow

        return self.subwin


class ChatWindow:

    """
    CHAS Chat window, used for text interface with CHAS
    """

    def __init__(self, chas, win):

        self.chas = chas  # CHAS Instance

        self.win = curses.newwin(0, 0)  # Curses window
        self._history = []  # All inputs entered
        self.test = None

        cords = win.getmaxyx()  # Max coordinates of the master window

        self.max_y = cords[0]  # Height of window
        self.max_x = cords[1]  # Width of window

        temp_inp = self.win.subwin(self.max_y - 4, 0)  # Creating subwindow for input widget
        self.inp = InputWindow(Border(temp_inp).border())  # Input window for getting text

        banner = self.win.subwin(10, self.max_x, 0, 0)  # Window for banner information

        self.banner = Border(banner).border()  # Generating border for the banner

        text = self.win.subwin(self.max_y - 15, self.max_x, 11, 0)  # Window for showing information

        self.text = Border(text).border()  # Adding border to text

        self.exit = 'exit'  # Exit keyword
        self.ban_text = '''+================================================+
C.H.A.S Text Interface system Ver: {}
Welcome to the C.H.A.S Text Interface System!
Please make sure your statements are spelled correctly.
C.H.A.S is not case sensitive!
Type 'help' for more details
'''.format('[[NOT IMPLEMENTED]]')

        self._init_screen()

    def _init_screen(self):

        """
        Initialise screen with preset strings
        :return:
        """

        # Start the banner

        self._render_banner()

        self.text.scrollok(True)
        self.text.idlok(True)

        self.banner.refresh()
        self.text.refresh()

    def _render_banner(self):

        """
        Function for rendering banner text
        :return:
        """

        self.banner.addstr(0, 0, "C.H.A.S Text Interface System Ver: {}".format(self.chas.version))
        self.banner.addstr(1, 0, "Welcome to the C.H.A.S Text Interface System!")
        self.banner.addstr(2, 0, "Type 'help' for information on available commands")
        self.banner.addstr(3, 0, "Plugins Loaded: {}".format(len(self.chas.extensions.get_extensions()['enabled'])))
        self.banner.addstr(4, 0, "Personality Loaded: {}".format(self.chas.person.selected.name))

        self.banner.refresh()

    def run(self):

        """
        Runs the chat window, and exits upon the keyword 'exit'
        :return:
        """

        while True:

            # Getting input from the user:

            inp = self.inp.input(prompt="Enter a statement:")

            # Adding input to screen and internal collection

            self._history.append(inp)

            self.add(inp, output='INPUT')

            # Checking for exit keyword:

            if self._check_exit(inp):

                # User wishes to exit

                return

            # Check CHAS handlers:

            val = self.chas.extensions.handel(inp, False, self)

            if val:

                # Extension was able to handel our input, continue,

                continue

            # Check remote, and see if their is a response

            data = self.chas.server.get({"voice": inp, "talk": False}, 2)

            print(data)

            if data["success"]:
                
                # Server was able to handel input
            
                self.add(data['resp'], output="REMOTE")
                
                continue

            # Extensions were not able to handel our input, pass information on to personality

            self.chas.person.handel(inp, False, self)

            continue

    def _check_exit(self, inp):

        """
        Checks if the input is the exit keyword
        :param inp: Input from user
        :return: Boolean determining if input is exit keyword
        """

        if self.exit == inp:

            return True

        return False

    def add(self, thing, output='OUTPUT'):

        """
        Adds text to screen, each entry is on a new line
        :param thing: String to add
        :param output: Information to add before the string
        :return:
        """

        # Formatting output value

        val = '[' + str(output.rstrip()) + ']:'

        # Adding input to window

        final = val + str(thing.rstrip()) + '\n'

        self.text.addstr(final)

        # Refreshing window

        self.text.refresh()
