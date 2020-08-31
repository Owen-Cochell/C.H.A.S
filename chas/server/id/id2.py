
from id.idhandle import IDHandle
from chaslib.resptools import key_search

# ID Handel for voice actions


class DummyWindow:

    """
    CHAS Dummy window to collect output
    """

    def __init__(self):

        self.output = []  # Output of window

    def add(self, mesg, output='OUTPUT'):

        # Add message to the internal collection

        self.output.append(mesg)

    def collect(self):

        """
        Combines strings in internal collection
        :return:
        """

        return "".join(self.output)


class VoiceHandel(IDHandle):

    def __init__(self):

        super(VoiceHandel, self).__init__('Voice Handler',
                                          'Handler for voice actions',
                                          2)

    def _gen_response(self, voice, val):

        return {"success": val, "resp": voice}

    def handel(self, dev, data):

        # Handel Method for voice actions  

        voice_str = data['voice']
        talk = data['talk']

        # Creating dummy window

        print("Creating dummy window:")

        dummy = DummyWindow()

        print("Sending input through handlers")

        val = self.chas.extensions.handel(voice_str, talk, dummy)

        print("Generating send data:")

        data = self._gen_response(dummy.collect(), val)

        print("Sending data:")

        dev.send(data, 2)
        
        return
