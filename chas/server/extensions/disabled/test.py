# A simple test file testing the extension service:

from chaslib.extension import Extension


class TestExtension(Extension):

    def __init__(self):

        super(TestExtension, self).__init__('Test-BaseExtension', 'A Simple test extension')
        self.test = 'This is a test!'

    def match(self, text, talk):

        # Function for matching text to operation

        text = text.lower()

        if text == 'test':

            self.method1()
            return True

        return False

    def method1(self):

        print(self.test)
        return

    def stop(self):

        # Stopping extension

        print("Stopping...")
        return
