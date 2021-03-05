
from id.idhandle import IDHandle
from chaslib.device import Device

# Handel for special requests


class DummyDevice(Device):

    # A dummy device that logs all attempted requests

    def __init__(self, inst, name, ip, port, sck):

        super(DummyDevice, self).__init__(inst, name, ip, port, sck)
        self.queue = []  # Message queue

    def send(self, content, id_num, encoding='utf-8'):

        self.queue.append(content)


class SpecialHandel(IDHandle):
    
    def __init__(self):
        
        super(SpecialHandel, self).__init__('Special Handler',
                                            'Handler for special requests',
                                            3)

    def _gen_dummy_device(self, dev):

        return DummyDevice(self.chas, dev.name, dev.ip, dev.port, dev.sock)

    def _gen_request(self, dev, content_uuid, content_id, content_type):
        
        return {'content-uuid': content_uuid,
                'content-status': 1,
                'content-id': content_id,
                'content-type': content_type,
                'content': dev.queue}

    def handel_server(self, device, data):

        content_uuid = data['content-uuid']
        content_id = data['content-id']
        content_status = data['content-status']
        content_type = data['content-type']
        content = data['content']
        
        if content_status == 1:
            
            # Handling a returning payload
        
            device.add_queue(data)
            
            return
        
        if content_type == 0:
            
            # Simple handel bypass

            handel = self.chas.net.handlers[content_id]

            dd = self._gen_dummy_device(device)

            handel.handel_server(dd, content)

            response = self._gen_request(dd, content_uuid, content_id, content_type)

            device.send(response, 3)
            
            return
