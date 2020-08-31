from id.idhandle import IDHandle
from chaslib.server import Server

# TODO: Error support for handlers/devices

# Handel for special requests


class DummyDevice(Server):

    # A dummy device that logs all attempted requests

    def __init__(self, chas, ip, port, sck, uuid):
        super(DummyDevice, self).__init__(chas, ip, port, sck, uuid)
        self.queue = []  # Message queue

    def send(self, content, id_num, encoding='utf-8'):

        self.queue.append(content)


class SpecialHandel(IDHandle):

    def __init__(self):

        super(SpecialHandel, self).__init__('Special Handler',
                                            'Handler for special requests',
                                            3)

    def _gen_dummy_device(self, dev):

        return DummyDevice(self.chas, dev.ip, dev.port, dev.sock, dev.uuid)

    def _gen_request(self, dev, content_uuid, content_id, content_type):

        return {'content-uuid': content_uuid,
                'content-status': 1,
                'content-id': content_id,
                'content-type': content_type,
                'content': dev.queue}

    def handel(self, dev, data):

        # Getting data here:

        content_uuid = data['content-uuid']
        content_id = data['content-id']
        content_status = data['content-status']
        content_type = data['content-type']
        content = data['content']

        if content_status == 1:

            # Handling a returning payload

            dev.add_queue(data)

            return

        if content_type == 0:

            # Simple handel bypass

            handel = self.chas.socket_client.handlers[content_id]

            dd = self._gen_dummy_device(self.chas.server)

            handel.handel(dd, content)

            response = self._gen_request(dd, content_uuid, content_id, content_type)

            dev.send(response, 3)

            return
