# A simple test file testing the extension service:

from chaslib.extension import Extension


class TestExtension(Extension):

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

        return False

    def method1(self):

        return self.test

    def stop(self):

        # Stopping extension

        print("Stopping...")
        return
