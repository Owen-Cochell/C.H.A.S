# A simple test file testing the extension service:

from chaslib.extension import BaseExtension
from chaslib.misctools import get_chas


class TestExtension(BaseExtension):

    def __init__(self):

        super(TestExtension, self).__init__('Test-Extension', 'A Simple test extension')
        self.test = 'Everything is working!'
        self.blank = None

    def match(self, text, talk, win):

        # Function for matching text to operation

        text = text.lower()

        if text == 'test':

            win.add(self.method1())
            return True

        if text == 'blank':
            
            # Return nothing
        
            return True

        if text == 'chasval':

            win.add(str(get_chas()))
            return True

        return False

    def method1(self):

        return self.test
