# A class representing the CHAS server

# TODO: Add ping, test for socketserver discrepancies, ...

import uuid


class Server:

    def __init__(self, chas, ip, port, sck, uu_id):

        self.chas = chas  # CHAS Masterclass
        self.ip = ip  # IP Address of the CHAS server
        self.port = port  # Websocket port of the CHAS server
        self.sock = sck  # Websocket
        self.uuid = uu_id  # UUID of this node
        self.auth = False  # Value determine if we are authenticated
        self.queue = []  # Message queue

    def send(self, content, id_num, encoding='utf-8'):

        # Function for sending data to CHAS server

        data = {'id': id_num,
                'uuid': self.uuid,
                'content': content}

        self.sock.write(data, encoding=encoding)

    def add_queue(self, data):

        self.queue.append(data)

        return

    def get(self, content, id_num, encoding='utf-8'):

        # Function for getting data from CHAS server

        content_uuid = str(uuid.uuid4())

        inner_data = {'content-uuid': content_uuid,
                      'content-id': id_num,
                      'content-status': 0,
                      'content-type': 0,
                      'content': content}

        data = {'id': 3,
                'uuid': self.uuid,
                'content': inner_data}

        self.sock.write(data)

        while True:

            for i in self.queue:

                if i['content-uuid'] == content_uuid:

                    # Found our request:

                    message = i['content']

                    self.queue.remove(i)

                    return message[0]
