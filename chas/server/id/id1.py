
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

        addr = sock.addr

        # Creating device object

        self.log.debug("Authenticating client {}:{} ...".format(addr[0], addr[1]))

        dev = Device(self.chas, 'undefined', addr[0], addr[1], sock)
        
        # Registering device with CHAS device management system

        self.chas.devices.register(dev)

        # Sending back confirmation and UUID

        self.log.debug("Sending authentication information ...")

        dev.send({'auth': True, 'uuid': str(dev.uuid)}, 1)

        return

    def handle_client(self, sock, data):

        # Checking if auth was successful...

        if data['auth']:

            # Auth was successful!

            # Creating new server object...

            self.log.debug("Successfully authenticated with the server!")

            addr = sock.addr

            sev = Server(self.chas, addr[0], addr[1], sock, data['uuid'])

            # Setting server object in CHAS lib

            self.chas.server = sev

            return

        else:

            # Auth failed.

            return