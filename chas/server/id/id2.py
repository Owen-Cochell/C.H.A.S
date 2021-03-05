import uuid

from id.idhandle import IDHandle
from chaslib.resptools import key_search

# ID Handel for voice actions


class DummyWindow:

    """
    CHAS Dummy window to collect output
    """

    def __init__(self):

        self.output = []  # Output of window

    def add(self, mesg, prefix='OUTPUT'):

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

        self.queue = []  # Queue of voice actions

    def _gen_response(self, voice, val):

        return {"success": val, "resp": voice}

    def handel_server(self, dev, data):

        # Handel Method for voice actions  

        voice_str = data['voice']
        talk = data['talk']

        # Creating dummy window

        dummy = DummyWindow()

        val = self.chas.extensions.handel(voice_str, talk, dummy)

        data = self._gen_response(dummy.collect(), val)

        dev.send(data, 2)
        
        return

    def _gen_uuid(self):

        return str(uuid.uuid4())

    def _gen_message(self, content):

        # Generate voice payload

        u_id = self._gen_uuid()

        data = {'voice': content, 'uuid': u_id}

        self.queue.append(data)

        return data

    def get_response(self, data):

        # Get voice response from server

        message = self._gen_message(data)
