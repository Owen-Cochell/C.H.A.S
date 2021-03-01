#!/bin/python
# ENTech SS
# This file contains misc. data for main script.
# This file dose not contain code for Home Config or the chatbot

import logging

from concurrent.futures import ThreadPoolExecutor

CHAS = None  # CHAS Masterclass


def get_chas():

    """
    Returns the CHAS masterclass for usage.
    Great if you don't have access to the instantiated CHAS masterclass

    :return: CHAS masterclass
    :rtype: CHAS
    """

    return CHAS


def set_chas(chas):

    """
    Sets the CHAS masterclass value.

    :param chas: CHAS Masterclass value to set
    :type chas: CHAS
    """

    global CHAS

    CHAS = chas


def get_logger(name):

    """
    Configures and returns a new logger using the specified name.

    We add the following handlers to the logger:

    FileHandler - Logs date, time, logger name, level
    CHASLogHandler - Logs level

    Each handler's level is specified using the values set in 'settings'py'.

    :param name: Name of the logger to add
    :type name: str
    :return: Logger instance
    :rtype: logging.Logger
    """

    # Configure the logger:

    log = logging.getLogger(name)

    # Set the logging level:

    log.setLevel(logging.DEBUG)

    # Create file handler:

    file_hand = logging.FileHandler(get_chas().settings.log_file)
    file_hand.setLevel(get_chas().settings.log_file_level)

    # Create CHAS handler:

    chas_log = CHASLogHandler()

    # Creating File formatter:

    file_format = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    file_hand.setFormatter(file_format)

    # Adding the handlers to logger:

    log.addHandler(file_hand)
    log.addHandler(chas_log)

    return log


class CHASLogHandler(logging.Handler):

    """
    A CHAS custom handler designed to send logging info to the CHAS Chat window.
    We do a lot of cool stuff here,
    mainly format text to fit into the terminal's handling.

    :param prefix: Prefix of the message to output
    :type prefix: str
    :param set_level: Value determining if we should set our own log level from the CHAS config
    :type set_level: bool
    """

    def __init__(self, set_level=True):

        super(CHASLogHandler, self).__init__()  # Call to our parent function

        self.chas = get_chas()  # CHAS value to work with

        if set_level:

            # Set our own level:

            self.setLevel(self.chas.settings.log_terminal_level)

        # Creating a formatter and attaching it to ourselves:

        self.setFormatter(logging.Formatter(fmt='%(levelname)s:%(message)s'))

    def handle(self, record: logging.LogRecord) -> None:

        """
        Sends the incoming log record to the CHAS output window.

        :param record: Incoming log record to send
        :type record: str
        """

        # Add the content with prefix to the CHAS output window

        self.chas.chat.add(self.format(record), prefix=record.name)


class CHASThreadPoolExecutor:

    """
    A CHAS Implementation of the ThreadPoolExecutor
    Keeps an internal state of all future abjects
    Ensures that pending tasks are canceled when the Executor is shutdown
    Error handling and other CHAS dependent features built in
    """

    def __init__(self, max_workers=None, thread_name_prefix="", initializer=None, initargs=()):

        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=thread_name_prefix,
                                        initializer=initializer, initargs=initargs)  # Internal ThreadPoolExecutor
        self._futures = []  # List of future objects

    def submit(self, fn, *args, **kwargs):

        """
        Wrapper to submit request to internal ThreadPoolExecutor
        :param fn: Function to be ran
        :param args: Any arguments to be passed
        :param kwargs: Any key word arguments to be passed
        :return:
        """

        temp = self._pool.submit(fn, *args, **kwargs)

        self._futures.append(temp)

        temp.add_done_callback(self._callback)

        return temp

    def map(self, func, *iterables, timeout=None, chunksize=1):

        """
        Wrappings for the internal ThreadPoolExecutor map() function
        :param func:
        :param iterables:
        :param timeout:
        :param chunksize:
        :return: Return value for the map() function
        """

        return self._pool.map(func, *iterables, timeout=timeout, chunksize=chunksize)

    def shutdown(self, wait=True, cancel_pending=True):

        """
        Shuts down the internal ThreadPoolExecutor
        Cancels any non-pending tasks
        :param wait: Weather to block until all *running* futures are completed
        :param cancel_pending Weather to cancel pending futures
        :return:
        """

        if cancel_pending:

            # Cancel all pending tasks, then shutdown

            num = 0

            while num < len(self._futures):

                # Attempt to cancel future, callback will handel the rest
                # Currently running tasks must be completed first

                # Getting future object

                future = self._futures[num]

                # Canceling future and getting return status

                stat = future.cancel()

                if stat:

                    # Future successfully removed, remaining on index and continuing

                    continue

                else:

                    # Future not removed, continuing

                    num = num + 1

                    continue

            self._pool.shutdown(wait=wait)

    def remove(self, future):

        """
        Removes a future from the internal collection
        :param future: Future object
        :return:
        """

        self._futures.remove(future)

    def _callback(self, fn):

        """
        Callback to be ran at the end of the future
        Removes future from internal collection and logs events accordingly
        :param fn: Future object automatically passed to the callback
        :return:
        """

        # Removing future from internal collection

        self._futures.remove(fn)

        # Handling future events

        if fn.cancelled():

            # Function canceled
            # TODO: Implement support for CHAS logging

            return

        if fn.done():

            # Getting error, if their is one

            error = fn.exception()

            if error:

                # Error occurred during runtime
                # TODO: Implement support for CHAS logging

                return

            else:

                # Task completed
                # TODO: Implement support for CHAS logging

                return

    def __enter__(self):

        """
        Support for context handling
        :return: self - For contex management
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        Called by context managers when exiting
        Does NOT handel exceptions encountered
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """

        self.shutdown(wait=True, cancel_pending=False)
        return False
