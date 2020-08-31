#!/bin/python
# ENTech SS
# This file contains misc. data for main script.
# This file dose not contain code for Home Config or the chatbot

import os
from concurrent.futures import ThreadPoolExecutor


def banner(ver, name):

    # Super cool banner

    print("        ______  __  __  ___     _____")
    print("       / ____/ / / / / /   |   / ___/")
    print("      / /     / /_/ / / /| |   \__ \ ")
    print("     / /____ / __  / / ___ |_ ___/ / ")
    print("     \____(_)_/ /_(_)_/  |_(_)____/  ")
    print("  Computerized Home Automation System")
    print("            Version: {}".format(ver))
    print("              {}".format(name))

    return


def main_menu(ver, name):

    # Main menu for C.H.A.S

    banner(ver, name)
    print("\nWelcome to the C.H.A.S Mainframe!\nPlease Select an option:")
    print("[1]: Display Network Info\n[2]: SSH Into A Server\n[3]: Open Home Config(NOT YET ACTIVE!)"
          "\n[4]: Open Chat System\n[5]: Display info\n[6]: Exit And Open A Shell")
    return


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
        Removes a future from thr internal collection
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
