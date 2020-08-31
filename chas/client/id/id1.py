
from id.idhandle import IDHandle
from chaslib.server import Server

# ID Handel for authentication system


class AuthHandel(IDHandle):

    def __init__(self):

        super(AuthHandel, self).__init__('Authentication Handler',
                                         'Handler for managing client authentication',
                                         1)
        self.id_num = 1

    def handel(self, sock, data):

        # Handel method for authentication

        # Checking if auth was successful...

        print("In auth handler...")
        print(sock)

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
