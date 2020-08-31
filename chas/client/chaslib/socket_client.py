import selectors
import socket
import pkgutil
import inspect
import threading

from chaslib.socket_lib import CHASocket


class SocketClient:

    def __init__(self, chas, host, port):

        self.chas = chas  # CHAS Instance
        self.running = False  # Value determining if the Socket Client is running
        self.host = host  # Hostanme of the CHAS server
        self.port = port  # Port num of the CHAS server
        self.sel = selectors.DefaultSelector()
        self.sock = None  # CHAS socket connected to the CHAS server
        self.handlers = []  # List of ID handlers
        self.thread = None  # Threading object

    def start_socket_client(self):

        # Function for starting the Socket Client

        self.running = True

        self.parse_handlers()

        self.thread = threading.Thread(target=self._sc_event_loop)
        self.thread.daemon = True
        self.thread.start()

        return

    def stop_socket_client(self):

        self.running = False

        self.thread.join()

    def _start_connection(self):

        addr = (self.host, self.port)
        # print(f"Starting connection to {addr}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 10000)

        self.sock.connect_ex(addr)

        self.sock.setblocking(False)

        events = selectors.EVENT_READ
        message = CHASocket(self.sel, self.sock, addr)
        self.sel.register(self.sock, events, data=message)

        message.write({'id': 1, 'uuid': None, 'content': None})

    def _get_id(self, hand):

        return hand.id_num

    def parse_handlers(self):

        # Function for parsing and loading ID Handlers

        direct = [self.chas.settings.id_dir]

        try:

            for finder, name, _ in pkgutil.iter_modules(direct):

                mod = finder.find_module(name).load_module(name)

                for member in dir(mod):

                    obj = getattr(mod, member)

                    if inspect.isclass(obj):

                        for parent in obj.__bases__:

                            if 'IDHandle' is parent.__name__:

                                # Appending CHAS to handler

                                obj.chas = self.chas

                                self.handlers.append(obj())

        except:

            # An error has occurred

            return

        self.handlers.sort(key=self._get_id)

        print(self.handlers)

        return

    def _sc_event_loop(self):

        self._start_connection()

        print("In socket server event loop...")

        while self.running:

            events = self.sel.select(timeout=1)

            for key, mask in events:

                message = key.data

                try:

                    if mask & selectors.EVENT_READ:

                        data = message.read()

                        #print(message)
                        self.handler(data, message)

                except Exception as e:

                    print(f"An error occurred: {e}")
                    message.close()

            if not self.sel.get_map():

                pass

    def handler(self, data, sock):

        uuid = data['uuid']
        req_id = data['id']
        content = data['content']
        hand = self.handlers[req_id]
        server = self.chas.server

        if req_id == 1:

            # Authenticating...

            print("Sending to auth handler:")

            hand.handel(sock, content)

            return

        hand.handel(server, content)
