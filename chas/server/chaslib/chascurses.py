import curses
import curses.panel
from math import ceil, floor
import threading
import queue

"""
CHAS Curses wrappings.
Includes special curses operations,
As well as custom curses windows to use.
The most important bit is the CHASWindow, which should 
act as the parent for all CHAS curses operations .
"""


class CHASWindow:

    """
    Custom CHAS Window.
    Handles the following actions:
    1. Writing content to a window
    2. Creating subwindows
    3. Handling borders/headers/subheaders
    4. Handling colors and text attributes
    5. Getting inputs and using callbacks to handel inputs
    6. Rendering content at specific locations on the screen

    #TODO: Look at these
    Things I would like supported, but are not critical:

    1. Mouse Support
    2. Better interface for handling color and attributes
    """

    # Constants for defining render location:

    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3
    CENTERED = 4

    def __init__(self, win):

        self.win = win  # Curses window to do our operations on, provided to us
        self.color = False  # Value determining if we have color
        self._calls = {}  # List of callbacks to be called given a keypress

        max_y, max_x = win.getmaxyx()

        self.max_x = max_x  # Maximum X cordnet
        self.max_y = max_y  # Maximum Y cordnet

        self.parent = None  # Parent window, used for bordering so we can keep track of it.
        self.header = None  # Header window
        self.sub_header = None  # Sub-header window

        self._init_screen()  # Initialise the screen with good curses defaults

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

        # Start Keypad handling

        self.win.keypad(True)

        # Allowing scrolling

        self.win.scrollok(True)

        # Allow hardware line editing facilities

        self.win.idlok(True)

        # Checking for color capacities

        if curses.has_colors():

            # Terminal has colors, enabling

            curses.start_color()
            self.color = True

    @staticmethod
    def _get_start_cords(start, max_y, max_x, y_len, x_len):

        """
        Calculates the starting cordnets for multiple places on the screen
        :param start: Location to render content
        :param max_y: Maximum y value
        :param max_x: Maximum x value
        :param y_len: Height of content to render
        :param x_len: Length of content to render
        :return: Starting y cordnet, starting x cordnet
        """

        if start == CHASWindow.TOP_LEFT:

            # User wants content in the upper left hand corner: 0, 0

            return 0, 0

        if start == CHASWindow.TOP_RIGHT:

            # User wants content in the upper right hand corner

            return 0, max_x - x_len

        if start == CHASWindow.BOTTOM_LEFT:

            # User wants content in bottom left hand corner

            return max_y - y_len, 0

        if start == CHASWindow.BOTTOM_RIGHT:

            # User wants content in bottom right hand corner

            return max_y - y_len, max_x - x_len

        if start == CHASWindow.CENTERED:

            # User wants content centered

            return (ceil(max_y / 2)) - (ceil(y_len / 2)), (ceil(max_x / 2)) - (ceil(x_len / 2))

    def add_callback(self, key, call, pass_self=False, args=None):

        """
        Adds callback to be called when specified key is pressed
        :param key: Key to be pressed, can be string or list, special characters included
        :param call: Function to be called
        :param pass_self: Value determining if we should pass this object to the callback.
        :param args: Args to be passed to the function
        :return:
        """

        if args is None:

            args = []

        if pass_self:

            args = [self] + args

        # Convert key to string

        if type(key) == list:

            # Working with a list

            for val in key:

                if type(val) == str:

                    # Convert string into ascii value

                    val = ord(val)

                self._calls[val] = {'call': call, 'args': args}

            return

        # Working with a single string here

        if type(key) == str:

            # Convert string into ascii value

            key = ord(key)

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

            # Running callback, with args specified

            func(*args)

            return True

        return False

    def _get_input(self):

        """
        Gets input from curses directly and returns it
        :return: Curses input
        """

        # Getting keypress and returning it

        return self.win.getch()

    def refresh(self):

        """
        Refreshes the curses screen.
        We also refresh the parent, and any headers
        :return:
        """

        if self.parent is not None:

            self.parent.refresh ()

        if self.header is not None:

            self.header.refresh()

        if self.sub_header is not None:

            self.sub_header.refresh()

        self.win.refresh()

    def addstr(self, content, ystart=-1, xstart=-1, position=-1, attrib=None):

        """
        Renders content on the screen.
        Supports rendering content at specific cordnets or positions
        :param content: Content to render
        :param ystart: starting y cordnet
        :param xstart: starting x cordnet
        :param position: Position to render content
        :param attrib: Attributes to apply to the text
        :return: Normal curses returncodes
        """

        if attrib is None:

            attrib = []

        if position != -1:

            # We want to render in a special location

            x_len = len(content)
            y_len = 1

            if len(content) >= self.max_x:

                # Content is bigger than lines, must figure out how many lines it takes up

                y_len = ceil(len(content) / self.max_x)
                x_len = self.max_x

            ystart, xstart = self._get_start_cords(position, self.max_y, self.max_x, y_len, x_len)

            if position == CHASWindow.BOTTOM_RIGHT and x_len < self.max_x:

                # We have to do some special formatting stuff to get the cursor to work

                self.win.addstr(ystart, xstart - 1, content, *attrib)

                return self.win.insstr(ystart, xstart - 1, " ")

            return self.win.addstr(ystart, xstart, content, *attrib)

        if ystart != -1 and xstart != -1:

            # user wants to render content at specific cordnets

            return self.win.addstr(ystart, xstart, content, *attrib)

        # Lets curses handel it, user dosen't care

        return self.win.addstr(content, *attrib)

    def bkgd(self, val):

        """
        Changes the window background to a specified value
        :param val: Value to set the background to
        :return: standard curses return
        """

        return self.win.bkgd(val)

    def border(self, ls=0, rs=0, ts=0, bs=0, tl=0, tr=0, bl=0, br=0, top_line='-', bottom_line='-',
               header_len=0, sub_len=0):

        """
        Generates the boarder and sets the necessary parameters to the new values.
        We also use this function to generate headers and sub-headers.
        Headers can be as tall as the user wants, and support all CHASWindow features.
        Content on the screen may be removed or messed up for borders and headers,
        So this should be called before any content is written to the window.
        :param ls: Left Side
        :param rs: Right Side
        :param ts: Top
        :param bs: Bottom
        :param tl: Upper left cornet
        :param tr: Upper right corner
        :param bl: Bottom left corner
        :param br: Bottom right corner
        :param top_line: Character used for rendering line for header
        :param bottom_line: Character used for rendering line for sub-header
        :param header_len: Height of header
        :param sub_len: Height of sub-header
        :return:
        """

        # Rendering border

        self.win.border(ls, rs, ts, bs, tl, tr, bl, br)

        self.win.refresh()

        self.parent = self.win

        if header_len > 0:

            # User wants to render in a header

            self.header = CHASWindow.create_subwin_at_cord(self.win, header_len, self.max_x - 2, 1, 1)

            # Now we draw the vertical line beneath the window:

            self.parent.hline(header_len + 1, 1, top_line, self.max_x - 2)

            self.header.refresh()

        if sub_len:

            # User wants to render in a sub-header

            self.sub_header = CHASWindow.create_subwin_at_cord(self.win, sub_len, self.max_x - 2,
                                                               self.max_y-1-sub_len, 1)

            # Draw the sub-header line:

            self.parent.hline(self.max_y-2-sub_len, 1, bottom_line, self.max_x-2)

            self.sub_header.refresh()

        # Creating subwindow

        max_y, max_x = self.parent.getmaxyx()

        self.win = self.parent.derwin((max_y - 3 - sub_len if sub_len > 0 else max_y - 2), max_x - 2,
                                      1 + (header_len + 1 if header_len > 0 else 0), 1)

        self.max_y, self.max_x = self.win.getmaxyx()

    def clear(self):

        """
        Clears all content from the curses window.
        :return: Standard curses returncode
        """

        return self.win.erase()

    def get_input(self, return_ascii=False, ignore_special=False):

        """
        Gets key from curses, sends it though the callbacks, and returns it if not a callback
        :param return_ascii: Value determining if we should return the ascii number of the key
        :param ignore_special: Determines if we should ignore special characters(ASCII values > 255)
        :return: Key that isn't handled by a callback
        """

        key = self._get_input()

        if self._handel_key(key):

            # Key was handled by a callback, return nothing

            return False

        if ignore_special and key > 255:

            # Key is a special key that we don't care about:

            return False

        if return_ascii:

            return key

        return chr(key)

    @classmethod
    def create_subwin_at_pos(cls, win, y_len, x_len, position=0):

        """
        Creates a centered subwindow using the window provided
        :param win: curses window
        :param y_len: height of window to create
        :param x_len: width of window to create
        :param position: Position to render the subwindow, defaults to upper left
        :return: CHAS Window object
        """

        # Get cords:

        max_y, max_x = win.getmaxyx()

        start_y, start_x = cls._get_start_cords(position, max_y, max_x, y_len, x_len)

        # Creating subwindow:

        newwin = win.derwin(y_len, x_len, start_y, start_x)

        return cls(newwin)

    @classmethod
    def create_subwin_at_cord(cls, win, y_len, x_len, starty, startx):

        """
        Creates a subwindow from the window provided at the cordnets provided
        :param win: Window to create subwindow from
        :param starty: Starting y cordnet
        :param startx: Starting x cordnet
        :param y_len: y length
        :param x_len: x length
        :return:
        """

        return cls(win.derwin(y_len, x_len, starty, startx))


class InputWindow(CHASWindow):

    """
    CHAS Input window
    Allows for the input of multiple characters, and scrolling
    Will use the ENTIRE window
    """

    def __init__(self, win):

        self.win = win  # Curses window provided

        super(InputWindow, self).__init__(win)  # Passing window to super class

        self.run = True  # Value determining if we are capturing input

        self.curs_x = 0  # Cursor x position
        self.curs_y = 0  # Cursor y position

        self.scroll = 0  # Number of lines we scrolled down

        self.inp = []  # Input data, each entry is a separate character

        self.prompt_len = 0  # Prompt for input system

        # Enabling cursor

        curses.curs_set(True)

        # Adding the necessary callbacks

        self.add_callback(curses.KEY_RIGHT, self._increment_cursor)
        self.add_callback(curses.KEY_LEFT, self._decrement_cursor)
        self.add_callback(curses.KEY_UP, self._decrement_cursor_line)
        self.add_callback(curses.KEY_DOWN, self._increment_cursor_line)
        self.add_callback([curses.KEY_BACKSPACE, 8], self._decrement_delete)
        self.add_callback([curses.KEY_ENTER, 10, 13], self._stop)

    def input(self, prompt="", add=''):

        """
        Starts recording input from user
        :param prompt: Prompt to display
        :param add: Adds the specified input to the window. Unlike the prompt, can be edited.
        :return:
        """

        # Resetting the object

        self._reset_object()

        # Getting the length of the prompt and setting it

        self.prompt_len = len(prompt)

        for i in list(prompt):

            # Adds the prompt to the internal collection:

            self.inp.append(i)

        self.curs_x = self.prompt_len

        for i in list(add):

            # Adds the editable content to the internal collection:

            self.inp.append(i)

        self._render()

        while self.run:

            # Getting key

            key = self.get_input(ignore_special=True)

            # Interpreting key

            if not key:

                # Key has been handled, render screen and continue

                self._render()

                continue

            # Key has not been handled, is string we can work with

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
        self.run = True  # Setting run value to True

        self.curs_x = 0  # Setting cursor x to 0
        self.curs_y = 0  # Setting cursor y to 0

        self.scroll = 0  # Setting scroll to zero

        self.win.erase()  # Clears the window

        self.win.refresh()  # Refreshes window to make changes final

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

    def _decrement_delete(self):

        """
        Decrements the cursor and deletes the character at the position,
        effectively deleting the previous character
        :return:
        """

        # Moving the cursor back

        self._decrement_cursor()

        # Deleting the character

        self._delete()

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

        # TODO: Remove this section
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

    def _stop(self):

        """
        Stops the input and any services that need to be stopped.
        :return:
        """

        self.run = False


class ChatWindow(CHASWindow):

    """
    CHAS Chat window, used for text interface with CHAS
    """

    def __init__(self, win):

        super(ChatWindow, self).__init__(win)

        self.chas = None  # CHAS Instance
        self._history = []  # All inputs entered
        self.test = None

        self.inp = InputWindow.create_subwin_at_cord(self.win, 4, self.max_x, self.max_y - 4, 0)  # Creating input win
        self.inp.border()  # Adding border to banner

        self.banner = CHASWindow.create_subwin_at_cord(self.win, 10, self.max_x, 0, 0)  # Creating banner window
        self.banner.border()  # Adding border to banner

        self.text = CHASWindow.create_subwin_at_cord(self.win, self.max_y-15, self.max_x, 11, 0)  # Text window
        self.text.border()  # Adding border to text

        self.exit = 'exit'  # Exit keyword
        self.ban_text = '''+================================================+
C.H.A.S Text Interface system Ver: {}
Welcome to the C.H.A.S Text Interface System!
Please make sure your statements are spelled correctly.
C.H.A.S is not case sensitive!
Type 'help' for more details
'''.format('[[NOT IMPLEMENTED]]')

        self._init_screen()

        self.banner.refresh()
        self.text.refresh()

    def _render_banner(self):

        """
        Function for rendering banner text
        :return:
        """

        self.banner.clear()

        self.banner.addstr("C.H.A.S Text Interface System Ver: {}".format(self.chas.version), 0, 0)
        self.banner.addstr("Welcome to the C.H.A.S Text Interface System!", 1, 0)
        self.banner.addstr("Type 'help' for information on available commands", 2, 0)
        self.banner.addstr("Plugins Loaded: {}".format(len(self.chas.extensions.get_extensions()['enabled'])), 3, 0)
        self.banner.addstr("Personality Loaded: {}".format(self.chas.person.selected.name), 4, 0)

        self.banner.refresh()

    def run(self):

        """
        Runs the chat window, and exits upon the keyword 'exit'
        :return:
        """

        while True:

            self._render_banner()

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

            # Extensions were not able to handel our input, pass information on to personality

            self.chas.person.handel(inp, False, self)

            continue

    def input(self):

        """
        Gets input from user and returns it
        :return: User input
        """

        while True:

            # Render in the banner:

            self._render_banner()

            # Getting input from the user:

            inp = self.inp.input(prompt='Enter a statement:')

            # Adding input to screen and internal collection:

            self._history.append(inp)

            self.add(inp, output='INPUT')

            # Returning input

            return inp

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


class ScrollWindow(CHASWindow):

    """
    A curses window for handling content scrolling.
    """

    def __init__(self, win):

        # Constructs the CHASWindow

        super(ScrollWindow, self).__init__(win)

        self.pos = 0  # Scroll position we are at

        self.content = []  # Content to render
        self.running = False  # Value determining if we are running

        self.thread = None  # Threading instance for frontend

        self.keys = queue.Queue()  # Queue for holding keypress

        # Adding callbacks:

        self.add_callback(curses.KEY_DOWN, self._increment_scroll)
        self.add_callback(curses.KEY_UP, self._decrement_scroll)
        self.add_callback('r', self._render_content)
        self.add_callback([curses.KEY_END, curses.KEY_EXIT, 'e', 'q'], self.stop)

    def get_key(self, block=True, timeout=None):

        """
        Gets a key from the key queue
        :return: Key from queue, or common queue returncodes
        """

        return self.keys.get(block=block, timeout=timeout)

    def run_display(self, content):

        """
        Starts a thread to render in front end, and allow the backend to continue to operate
        :param content: Content to render
        :return:
        """

        if type(content) == list:

            # Working with a list of content:

            for i in content:

                temp = self._split_content(i)

                for v in temp:

                    self.content.append(v)

        else:

            self.content.append(self._split_content(content))

        print(self.content)

        self.thread = threading.Thread(target=self.display_content)

        self.running = True

        self.thread.start()

    def stop(self):

        """
        Stops the thread and stops rendering content
        :return:
        """

        if not self.running:

            return

        self.running = False

    def block(self):

        """
        Blocks until the scroll window is stopped by the user
        :return:
        """

        self.thread.join()

    def is_running(self):

        """
        Checks if the thread is still running
        :return: True for is running, False for is not running
        """

        return self.running

    def display_content(self):

        """
        Displays content on a scrollable window.
        Can move up or down to see content.
        Content MUST be in list form, each value being on a separate line.
        :return:
        """

        self.win.refresh()

        while self.running:

            # Get key and handel it:

            key = self.get_input()

            print("Key Pressed: {}".format(key))

    def add_content(self, content):

        """
        Adds content to the internal collection.
        Handles the formatting of newlines and splitting content that is too big for the screen.
        :param content: Content to add
        :return:
        """

        split = []

        # Getting split content:

        if type(content) == list:

            # Working with a list:

            for i in content:

                temp = self._split_content(i)

                for v in temp:

                    split.append(v)

        else:

            split = self._split_content(content)

        # Adding content to the end of the collection

        for i in split:

            self.content.append(i)

        return

    def clear(self):

        """
        Clears the internal collection.
        :return:
        """

        self.content = []

    def _split_content(self, content):

        """
        Splits up strings based on newlines, and if they are too big for the window.
        :param content: Content to split
        :return:
        """

        lines = content.split('\n')
        new = []

        for line in lines:

            # Check if line is larger than the width

            if len(line) > self.max_x:

                # Content is bigger, do something about it

                num = ceil(len(line) / self.max_x)

                for i in range(num):

                    # Iterate over each section and separate it

                    new.append(line[i*self.max_x:(i+1)*self.max_x])

                continue

            new.append(line)

        print("Split content: {}".format(new))

        return new

    def _increment_scroll(self):

        """
        Increments the scroll by one, does not increase if it is greater than the content provided
        :return:
        """

        if len(self.content) - 1 > self.pos:

            # Increase the position, it is valid

            self.pos = self.pos + 1

        # Render the content

        print("Position: {}".format(self.pos))

        self._render_content()

    def _decrement_scroll(self):

        """
        Decrements the scroll by one, does not decrease if it is zero.
        :return:
        """

        if self.pos > 0:

            self.pos = self.pos - 1

        # Render the content

        self._render_content()

    def _render_content(self):

        """
        Renders the content to the screen based on the position.
        We make a point not to touch the bottom line, as scrolling messes things up.
        :return:
        """

        # Clearing window:

        self.win.erase()

        # Getting content to render:

        content = self.content[self.pos:self.max_y+self.pos - 1]

        for num, val in enumerate(content):

            self.addstr(val, num, 0)

        self.win.refresh()


class OptionWindow(CHASWindow):

    """
    Displays a list of options to the user.
    Support simple selection, boolean selection, and value selection.  
    """

    NULL_OPTION = 0
    EXIT_OPTION = 1
    SIMPLE_SELECT = 2
    TOGGLE_SELECT = 3
    VALUE_SELECT = 4
    MANUAL_SELECT = 5
    SUB_MENU = 6

    def __init__(self, win):

        super(OptionWindow, self).__init__(win)

        self.option_position = 0  # Option to select on screen

        self.scroll_position = 0  # Scroll level we are currently on

        self.options = []  # List of options, must abide by the CHASOptions convention

        self.run = True  # Value determining if we are running

        self.simple = False  # Determining if we are working with Simple Selection

        self.selected = None  # Selected option, used only for simple selection

        # Adding necessary callbacks:

        self.add_callback(['q', 'e'], self._stop)
        self.add_callback(curses.KEY_UP, self._decrement_cursor)
        self.add_callback(curses.KEY_DOWN, self._increment_cursor)
        self.add_callback([curses.KEY_ENTER, 10, 13], self._handel_selection)
        self.add_callback('r', self.refresh)

    def display(self, no_return=False, title=None):

        """
        Displays the options in our collection, run until we exit
        :param no_return: Determines if we should return values. Great for menus that might need to display
        content multiple times.
        :param title: Will render in a title in the header of the window.
        :return:
        """

        # We add an Exit value to the window, so the user can easily exit

        self.add_option('Exit', OptionWindow.EXIT_OPTION)

        # Check if user wants header, render one if necessary:

        if title is not None:

            print(self.win.border)

            self.border(header_len=1, sub_len=1)

            self.header.addstr(title)

        # Starting the window:

        self.run = True

        while self.run:

            # Getting key from user:

            self._render()

            key = self.get_input()

        self.options.pop(len(self.options) - 1)

        if no_return:

            # Return nothing, we are done here

            return

        if self.simple:

            # Simple selection, return selected value

            return self.selected

        # Otherwise, we return the options, they are edited as the user wants them to be.

        return self._convert()

    def add_option(self, name, option_type, desc='', value=None):

        """
        Adds a singular option to the collection.
        If no value is specified, then a default one will be selected.
        :param name: Name of the option
        :param option_type: Type of the option
        :param desc: Description of the option
        :param value: Value of the option
        :return:
        """

        if option_type == OptionWindow.SIMPLE_SELECT:

            # Working with simple select, make sure this object knows that

            self.simple = True

        if option_type == OptionWindow.VALUE_SELECT:

            # We need to use a special format for selecting values:

            value = [value, value[0]]

        if option_type == OptionWindow.SUB_MENU and type(value) is not OptionWindow:

            # We need to create an OptionWindow instance to work with:

            new = OptionWindow.create_subwin_at_pos(self.win, self.max_y - 1, self.max_x - 1)

            new.add_options(value)

            value = new

        self.options.append({'name': name, 'type': option_type, 'desc': desc, 'value': value})

    def add_options(self, options):

        """
        Gets a list/dictionary of options and creates an option menu that conforms to the list/dictionary format.
        If the value provided is a list of values, then OptionWindow will make a simple
        selection menu with those values.
        If the value provided is a dictionary, then OptionWindow will attempt to create options with the best
        corresponding values.
        If you don't like OptionWindow's interpretation of your values, you should add them manually.
        :param options: List/dictionary of options
        :return:
        """

        if type(options) == list:

            # Working with a list, make them all simple selection

            for opt in options:

                self.add_option(opt, OptionWindow.SIMPLE_SELECT)

        if type(options) == dict:

            # Working with dict, dynamically select the appropriate option for each value

            for opt in options:

                # Check which type opt is, and handel accordingly

                val = options[opt]

                if type(val) == str:

                    # Create a manual selection option

                    self.add_option(opt, OptionWindow.MANUAL_SELECT, value=val)

                    continue

                if type(val) == list:

                    # Create a Value Select option

                    self.add_option(opt, OptionWindow.VALUE_SELECT, value=val)

                    continue

                if type(val) == bool:

                    # Create a Toggle Select

                    self.add_option(opt, OptionWindow.TOGGLE_SELECT, value=val)

                if type(val) == dict:

                    # Create a sub-menu

                    new = OptionWindow.create_subwin_at_pos(self.win, self.max_y - 1, self.max_x - 1)

                    new.add_options(val)

                    self.add_option(opt, OptionWindow.SUB_MENU, value=new)

                    continue

                if val is None:

                    # Create a Null Selection

                    self.add_option(opt, OptionWindow.NULL_OPTION)

                    continue

    def get_options(self):

        """
        Calls the underlying _convert method and returns the internal collection of options in dictionary format.
        :return: Dictonary of options
        """

        if self.simple:

            # Simple selection, return selected

            return self.selected

        # Something else, return it:

        return self._convert()

    def _convert(self):

        """
        Converts the internal collection of options into dictionary format.
        :return:
        """

        # Iterate over each option and handel them accordingly

        done = {}

        for opt in self.options:

            if opt['type'] == OptionWindow.EXIT_OPTION or opt['type'] == OptionWindow.NULL_OPTION:

                # We don't care about these values, continue:

                continue

            if opt['type'] == OptionWindow.VALUE_SELECT:

                # Value uses a special format, pull out the necessary values:

                done[opt['name']] = opt['value'][1]

                continue

            if opt['type'] == OptionWindow.SUB_MENU:

                # We need to pull the options out of the sub menu:

                done[opt['name']] = opt['value'].get_options()

                continue

            done[opt['name']] = opt['value']

        return done

    def _calc_position(self):

        """
        Calculates the position in the list based on scroll level and scroll position
        :return: Index of selected position in the list
        """

        return (self.scroll_position * self.max_y) + self.option_position

    def _increment_cursor(self):

        """
        Moves the cursor up 1, and scrolls the screen if necessary.
        :return:
        """

        if self.option_position < self.max_y - 1 and self.option_position + (self.scroll_position * self.max_y) < \
                len((self.options if len(self.options) > 1 else 2)) - 1:

            # Less than the window, move option selection up one.

            self.option_position = self.option_position + 1

            return

        if len(self.options) - 1 > (self.max_y * self.scroll_position) + self.option_position:

            # We have to scroll the window upwards

            self.scroll_position = self.scroll_position + 1

            self.option_position = 0

        return

    def _decrement_cursor(self):

        """
        Moves the cursor down 1, scrolls the screen if necessary.
        :return:
        """

        if self.option_position > 0:

            # We are good to move the option position down

            self.option_position = self.option_position - 1

            return

        # We have to scroll the window down:

        if self.scroll_position > 0:

            # Scroll the window down

            self.scroll_position = self.scroll_position - 1

            self.option_position = self.max_y - 1

            return

        return

    def _get_type_name(self, opt):

        """
        Gets a type name from the option provided.
        :param opt: Option provided.
        :return: Preview value   
        """

        opt_type = opt['type']

        if OptionWindow.TOGGLE_SELECT == opt_type:

            # Working with a toggle, determine if we are rendering true/false

            if opt['value']:

                # Render in a True

                return '[True]'

            return '[False]'

        if OptionWindow.MANUAL_SELECT == opt_type:

            # Render in 'Enter, subject to change

            return '[Enter]'

        if OptionWindow.SUB_MENU == opt_type or OptionWindow.VALUE_SELECT == opt_type:

            # Render in '>', subject to change

            return '[>]'

        # No special preview name required!

        return ''

    def _get_shortened_name(self, opt, num):

        """
        Gets a shortened name from the option given.
        This is calculated from the maximum x value, as well as the preview value.
        We also render in the number of the option, and take that into account for our shortening.
        """

        # Get type name here:

        type_name = self._get_type_name(opt)

        # Calculate stopping distance for the name

        stop = self.max_x - len(type_name) - (7 if num > 0 else 4) - (len(str(num)) if num > 0 else 0)

        # Returning shortened name:

        return ('[{}]:'.format(num) if num > 0 else '') + opt['name'][:stop] + \
               ('...' if stop < len(opt['name']) else '')

    def _render(self):

        """
        Renders the selected content to the screen.
        :return:
        """

        # Iterate over every relevant option and render it to the screen:

        self.win.erase()

        off = 0  # Offset to render numbers:

        for num, opt in enumerate(self.options[self.scroll_position * self.max_y:
                                  (self.scroll_position + 1) * self.max_y]):

            # Get shortened name(If necessary):

            if opt['type'] == OptionWindow.NULL_OPTION:

                # Don't render a option number, it is a null option!

                off = off + 1

            name = self._get_shortened_name(opt, num + 1 + (self.max_y * self.scroll_position) - off
                                            if opt['type'] != OptionWindow.NULL_OPTION else -1)

            # Get type name:

            type_name = self._get_type_name(opt)

            # Render option name to screen:

            self.addstr(name, num, 0, attrib=([curses.A_STANDOUT] if num == self.option_position else None))

            # Render Type Name to screen:
            # We render with some special tricks to ensure that the window does not scroll

            self.addstr(type_name, num, self.max_x - len(type_name) - 1)
            self.win.insstr(num, self.max_x - len(type_name) - 1, " ")

        # Refresh the screen, as we are done rendering.

        self.refresh()

    def _handel_selection(self):

        """
        User selected the option we are currently on, handle it and make any changes.
        We edit the options list directly.
        :return:
        """

        # Clearing window:

        self.clear()

        # Get index of option:

        index = self._calc_position()

        # Handel option:

        self.options[index] = self._handel_option(self.options[index])

        return

    def _handel_option(self, opt):

        """
        Handles the option selected, and does any actions necessary
        :return:
        """

        opt_type = opt['type']

        if OptionWindow.NULL_OPTION == opt_type:

            # This is a null option, do nothing

            return opt

        if OptionWindow.EXIT_OPTION == opt_type:

            # This is exit option, exit.
            # If simple selection, select the first option

            self._stop()

            if self.simple:

                return self.options[0]['name']

            return opt

        if OptionWindow.SIMPLE_SELECT == opt_type:

            # Simple selection, return value selected:

            self.run = False

            self.selected = opt['name']

            return opt

        if OptionWindow.TOGGLE_SELECT == opt_type:

            # Toggle the option on/off, return opposite

            opt['value'] = not opt['value']

            return opt

        if OptionWindow.VALUE_SELECT == opt_type:

            # Have the user choose from a list of options:

            # Create a new Option Menu, should be overlayed on top of ours:

            new = OptionWindow.create_subwin_at_pos(self.win, self.max_y - 1, self.max_x - 1)

            new.add_options(opt['value'][0])

            opt['value'][1] = new.display(title=opt['name'])

            print(opt)

            return opt

        if OptionWindow.MANUAL_SELECT == opt_type:

            # Have the user manually enter an option:

            # Create an input window:

            input_win = InputWindow.create_subwin_at_pos(self.win, int(self.max_y / 2), int(self.max_x / 2),
                                                         position=CHASWindow.CENTERED)

            # Create a border for viewing enjoyment:

            input_win.border(header_len=1, sub_len=1)

            input_win.header.addstr("Enter/Edit Value Below:")

            input_win.refresh()

            inp = input_win.input(add=opt['value'])

            if inp is None:

                return opt

            opt['value'] = inp

            return opt

        if OptionWindow.SUB_MENU == opt_type:

            # Open up the OptionWindow associated with the sub menu.
            # Don't return the content, we leave that to the converter.

            opt['value'].display(no_return=True, title=opt['name'])

            return opt

    def _stop(self):

        """
        Stops the OptionWindow.
        :return:
        """

        self.run = False
