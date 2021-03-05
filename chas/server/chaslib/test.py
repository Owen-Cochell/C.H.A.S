from chaslib.chascurses import *

from chaslib.sound.base import OutputHandler
from chaslib.sound.input import WaveReader
from chaslib.sound.out import PyAudioModule

import curses
from math import ceil
import time


def dummy(win, test):

    win.win.addstr("This is a test! You should have pressed F1!")
    win.win.addstr("Here is the argument supplied: {}".format(test))

    return


def callback_test(win):  # PASSED

    while True:

        # Creating CHAS windows

        chas = CHASWindow(win)

        # Adding callback for the F1 key

        chas.add_key(curses.KEY_F1, dummy, pass_self=True, args=['testing!'])

        # Getting input and printing input:

        inp = chas.get_input()

        if inp == 'q':

            return

        if inp:

            win.addstr(inp)


def center_test(win):  # PASSED

    # Create a centered window and write stuff to it

    win.bkgd('/')

    win.refresh()

    max_y, max_x = win.getmaxyx()

    print("Max X:" + str(max_x))
    print("Max Y:" + str(max_y))

    # Creating centred window:

    chas = CHASWindow.create_subwin_at_pos(win, 10, 50, position=CHASWindow.CENTERED)

    chas.win.bkgd(' ')
    chas.win.addstr("This is a test of the centered window!")

    chas.win.refresh()
    win.refresh()

    chas.get_input()


def single_position_test(win):  # PASSED

    # Renders text at multiple parts of the master window

    text = ['Top Left', 'Top Right', 'Bottom Left', 'Bottom Right', 'Centered']

    win.bkgd('/')

    chas = CHASWindow.create_subwin_at_pos(win, 20, 50, position=CHASWindow.CENTERED)

    chas.bkgd(' ')

    for num, val in enumerate(text):

        # Render text in window

        chas.addstr(val, position=num)

        chas.refresh()

        chas.get_input()

    win.getch()


def multi_position_test(win):  # PASSED

    # Renders windows at multiple points, and text at multiple points within them

    text = ['Top Left', 'Top Right', 'Bottom Left', 'Bottom Right', 'Centered']
    ntext = ['Top left', 'Top Right', 'Bottom Left', 'Bottom Right', 'Centered']
    wins = []

    win.bkgd('/')

    for i in range(5):

        # Create and render a window at a position

        new_win = CHASWindow.create_subwin_at_pos(win, 17, 50, position=i)

        new_win.bkgd(' ')

        wins.append(new_win)

        for num, val in enumerate(ntext):

            # Render content at locations in window

            new_win.addstr(val, position=num)

            new_win.refresh()

    #win.addstr(0, 0, "TESTING!")
    win.getch()


def position_wrap_test(win):  # PASSED

    # Wraps content around when using positions

    win.bkgd('/')

    chas = CHASWindow.create_subwin_at_pos(win, 17, 50, position=4)

    chas.bkgd(" ")

    thing = "THis text should be bigger than 17 characters! Don't believe me? Check out the curses window," \
            "Should take multiple lines if working correctly!"

    chas.addstr(thing, position=3)

    chas.refresh()

    win.getch()


def input_test(win):  # PASSED

    # Tests the CHAS input widget

    win.bkgd('/')

    win.refresh()

    inp = InputWindow.create_subwin_at_pos(win, 10, 50, position=CHASWindow.CENTERED)

    inp.bkgd(" ")

    thing = inp.input(prompt='Input:')

    print(thing)


def scroll_window_test(win):  # PASSED

    # Tests the CHAS scoll window

    win.bkgd('/')

    win.refresh()

    conwin = ScrollWindow.create_subwin_at_pos(win, 10, 50, position=ScrollWindow.CENTERED)

    conwin.bkgd(' ')

    content = []
    index = 0

    for i in range(100):

        content.append("This is value: {}".format(i))

    conwin.run_display(content)

    conwin.block()


def scroll_window_wrapping_test(win):  # PASSED

    # Tests the CHAS wrapping function

    content = ['THis should be on -\nMulitple lines!', 'This should be a multi line statement, as this '
                                                       'test is in fact very long. This should not hinder the '
                                                       'windows ability to not only handel it, but wrap it.',
               'This is - \n - Two lines!']

    win.bkgd('/')

    win.refresh()

    conwin = ScrollWindow.create_subwin_at_pos(win, 10, 10, position=ScrollWindow.CENTERED)

    conwin.bkgd(' ')

    conwin.run_display(content)

    conwin.block()


def border_test(win):

    # Tests the border feature of CHASWindow

    win.bkgd('/')

    win.refresh()

    chas = CHASWindow.create_subwin_at_pos(win, 20, 50, position=CHASWindow.CENTERED)

    chas.bkgd(' ')

    chas.border()

    chas.addstr("This should be in content window!")

    chas.refresh()

    chas.get_input()


def header_test(win):

    # Testing the header/sub-header functionality for CHASWindow

    win.bkgd('/')

    win.refresh()

    chas = CHASWindow.create_subwin_at_pos(win, 20, 50, position=CHASWindow.CENTERED)

    chas.bkgd(' ')

    chas.border(header_len=3, sub_len=3)

    chas.addstr("This should be in the content!")

    chas.header.addstr("This should be in the header!")

    chas.sub_header.addstr("This should be in the sub-header!")

    chas.refresh()

    chas.get_input()


def simple_selection_test(win):

    # Tests out the simple selection feature of CHAS OptionWindow

    options = []

    for i in range(0, 100):

        options.append("Option {}".format(i))

    win.bkgd('/')

    win.refresh()

    optionwin = OptionWindow.create_subwin_at_pos(win, 20, 50, position=OptionWindow.CENTERED)

    optionwin.bkgd(' ')

    optionwin.add_options(options)

    out = optionwin.display()

    print(out)


def mulit_selection_test(win):

    # Tests out the window selection types.

    options = {'Manual': 'Testing', 'Boolean': False, 'Value': ['1', '2', '3', '4'], 'Null': None, 'Sub':
               {'Manual': 'Testing', 'Boolean': False, 'Value': ['1', '2', '3', '4']},
               'This is a very long option name, and should be shortened accordingly. Seeing names like this in '
               'production should be very rare, but things like this could happen, so we need to be ready.': False}

    win.bkgd('/')

    win.refresh()

    optionwin = OptionWindow.create_subwin_at_pos(win, 20, 50, position=OptionWindow.CENTERED)

    optionwin.bkgd(' ')

    optionwin.add_options(options)

    opt = optionwin.display()

    print(opt)


def run_dummy():

    # Prints run dummy

    print("Run Dummy!")


def run_window_test(win):

    # Tests the run option

    win.bkgd('/')

    win.refresh()

    optionwin = OptionWindow.create_subwin_at_pos(win, 20, 50, position=OptionWindow.BOTTOM_LEFT)

    optionwin.bkgd(' ')

    optionwin.add_option("Run Dummy!", optionwin.RUN_OPTION, value=run_dummy)

    optionwin.display()


def all_tests(win):

    # Runs all tests

    tests = [callback_test, center_test, single_position_test, multi_position_test,
             position_wrap_test, input_test, scroll_window_test, scroll_window_wrapping_test, border_test, header_test,
             simple_selection_test, mulit_selection_test]

    for test in tests:

        test(win)

        win.erase()


def sound_test():

    # Tests the sound of CHAS audio

    #wav1 = WaveReader('/data/Data/Stash/Projects/chas/server/media/songs/talking_heads/wild.wav')
    wav2 = WaveReader('/data/Data/Stash/Projects/chas/server/media/sounds/listen.wav')
    wav2.loop = True

    out = PyAudioModule()
    out.special = True

    hand = OutputHandler()

    #thing = hand.bind_synth(wav1)
    thing2 = hand.bind_synth(wav2)

    hand.add_output(out)

    hand.start()

    #thing.start()

    #time.sleep(2)

    thing2.start()

    hand.join()


#curses.wrapper(run_window_test)
