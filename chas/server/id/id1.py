
from id.idhandle import IDHandle
from chaslib.device import Device, Server

# ID Handel for authentication actions


class AuthHandel(IDHandle):

    def __init__(self):

        super(AuthHandel, self).__init__('Authentication Handler',
                                         'Handler for managing authentication',
                                         1)

    def get_id(self):

        return 1

    def handel_server(self, sock, data):

        # Handel method for Authentication

        # Getting socket address information

        print("In auth handler")

        addr = sock.addr

        # Creating device object

        print("Creating device object:")

        dev = Device(self.chas, 'undefined', addr[0], addr[1], sock)
        
        # Registering device with CHAS device management system

        print("Registering device:")

        self.chas.devices.register(dev)

        # Sending back confirmation and UUID

        print("Sending authentication information...")

        dev.send({'auth': True, 'uuid': str(dev.uuid)}, 1)

        return

    def handel_client(self, sock, data):

        # Checking if auth was successful...

        if data['auth']:

            # Auth was successful!

            # Creating new server object...

            addr = sock.addr

            sev = Server(self.chas, addr[0], addr[1], sock, data['uuid'])

            # Setting server object in CHAS lib

            self.chas.server = sev

            return

        else:

            # Auth failed.

            return