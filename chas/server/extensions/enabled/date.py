# Extension that wraps the python datetime module

from chaslib.extension import Extension
import datetime
from chaslib.resptools import keyword_find, key_sta_find


class DateTime(Extension):

    def __init__(self):

        super(DateTime, self).__init__('Date-Time', 'Wrapper for the Datetime python module')
        self.datetime = datetime.datetime
        self.help = [{'date': 'Displays the date'},
                     {'number date': 'Displays the numerical date'},
                     {'time': "Displays the time"}]

    def match(self, mesg, talk, win):

        if keyword_find(mesg, ['date', 'day']):

            # User wants the date

            if keyword_find(mesg, ['number', 'numbers', 'intiger']):

                # User wants number date:

                win.add(self._get_number_date())

                return True

            win.add(self._get_word_date())

            return True

        if keyword_find(mesg, 'time'):

            # User wants the time

            win.add(self._get_time())

            return True

        return False

    def _get_inst(self):

        return datetime.datetime.now()

    def _get_time(self):

        return self._get_inst().strftime("%H:%M")

    def _get_word_date(self):

        inst = self._get_inst()

        day = int(inst.strftime("%d"))

        rest = inst.strftime("%A, %B {}, %Y")

        return rest.format(str(day) + self._get_ordinal(day))

    def _get_number_date(self):

        inst = self._get_inst()

        day = int(inst.strftime("%d"))

        rest = inst.strftime("%m/{}/%Y")

        return rest.format(str(day))

    def _get_ordinal(self, num):

        # Return proper ordinal

        num = num % 10

        if num == 1:

            return "st"

        if num == 2:

            return "nd"

        if num == 3:

            return "rd"

        return "th"
