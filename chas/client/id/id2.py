# Handler for voice    actions

from id.idhandle import IDHandle
import uuid


class VoiceHandel(IDHandle):

    def __init__(self):

        super(VoiceHandel, self).__init__('Voice Handler',
                                          'Handler for voice actions',
                                          2)
        self.queue = []  # Queue of voice actions

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



