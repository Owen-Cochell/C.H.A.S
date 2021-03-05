import selectors
import socket
import threading
import pkgutil
import inspect
import queue
import traceback

from chaslib.socket_lib import CHASocket
from chaslib.misctools import CHASThreadPoolExecutor, get_logger

# Packet is as follows:

# Post-header - Header - Data

# Let SS stand for Socket Server


def get_id(hand):

    return hand.id_num


class SocketServer:

    def __init__(self, chas, host, port):

        self.chas = chas  # Instance of the CHAS masterclass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Listening socket
        self.sel = selectors.DefaultSelector()  # Selector object
        self.host = host  # Hostname of our SS
        self.port = port  # Port of our SS
        self.listen_thread = None  # Reference to the SS listener thread
        self.write_thread = None  # Reference to the SS writer thread
        self.devices = self.chas.devices  # CHAS Device instance
        self.running = False  # Value determining if the ss is running
        self.handlers = []  # List containing handler info
        self.write_queue = queue.Queue()  # Write Queue object
        self.pool = CHASThreadPoolExecutor()  # Thread pool executor instance - For running handler code

        self.log = get_logger("CORE:NET")

    def _start_socket(self):

        # Starting a listening socket for accepting new connections

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 64000)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64000)

        self.sock.bind((self.host, self.port))
        self.sock.listen()

        self.log.debug(f"Listening on: {self.host}:{self.port}")

        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, data=None)

    def _accept_connection(self, sock):

        # Creating socket and registering it with the selector:

        conn, addr = sock.accept()

        self.log.debug(f"Accepted connection from: {addr}")

        conn.setblocking(False)
        message = CHASocket(self.sel, conn, addr, self.log)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def _ss_listener(self):

        # Main listen thread for the socket server

        self._start_socket()

        while self.running:

            events = self.sel.select(timeout=5)

            for key, mask in events:

                if key.data is None:

                    self._accept_connection(key.fileobj)

                else:

                    message = key.data

                    try:

                        if mask & selectors.EVENT_READ:

                            # Reading data from socket...

                            data = message.read()

                            # Starting task in ThreadPoolExecutor to handel request...

                            payload = {'sock': message, 'data': data}

                            self.pool.submit(self.handler, payload)

                            continue

                    except Exception as e:

                        self.log.error("Error during socket event loop: {}".format(e))

                        self.log.debug("Traceback: \n{}".format(traceback.format_exc()))
                        message.close()

    def _ss_write(self):

        """
        Socket Server writing thread
        """

        while self.running:

            # Pull a request from the queue:

            data = self.write_queue.get()

            # Checking if data is "None"

            if data is None:

                # Socket server is done writing

                return

            # Get necessary data:

            uuid = data['uuid']
            data = data['data']

            # Getting device from Devices

            dev = self.chas.devices.get_by_uuid(uuid)

            # Writing data to device

            dev.sock.write(data)

    def write(self, data, uuid):

        """
        Add data to the write queue to be written
        :param data: Data to be sent
        :param uuid: UUID of device to send data to
        :return:
        """

        self.write_queue.put({"uuid": uuid,
                              "data": data})

    def start(self):

        # Function for starting the ss listener thread and ss write thread.

        self.running = True

        self.log.debug("Parsing and loading handlers...")

        self.parse_handlers()

        # Defining listener thread

        self.log.debug("Starting listening thread...")

        self.listen_thread = threading.Thread(target=self._ss_listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        # Defining write thread:

        self.log.debug("Starting write thread...")

        self.write_thread = threading.Thread(target=self._ss_write)
        self.write_thread.daemon = True
        self.write_thread.start()

        return

    def stop(self):

        # Function for gracefully stopping the ss thread

        self.running = False

        # Joining listening thread

        self.log.debug("Stopping listening thread...")

        self.listen_thread.join()

        # Adding 'None' to write queue to kill write thread

        self.write_queue.put(None)

        # Joining write thread

        self.log.debug("Stopping write thread...")

        self.write_thread.join()

        # Shutting down handel thread

        self.log.debug("Stopping handler threads...")

        for hand in self.handlers:

            hand.stop()

        self.pool.shutdown()

    def parse_handlers(self):

        # Function for parsing and loading ID Handlers

        direct = [self.chas.settings.id_dir]

        try:

            for finder, name, _ in pkgutil.iter_modules(path=direct):

                # Loading module for inspection

                mod = finder.find_module(name).load_module(name)

                for member in dir(mod):

                    # Iterating over builtin attributes

                    obj = getattr(mod, member)

                    # Checking if object is a class

                    if inspect.isclass(obj):

                        # Iterating over parents

                        for parent in obj.__bases__:

                            # Chexking for IDHandel parent

                            if 'IDHandle' == parent.__name__:

                                # Binding CHAS to handler

                                obj.chas = self.chas

                                # Found a IDHandler

                                self.handlers.append(obj())

        except Exception as e:

            # An error has occured

            print(f"An error occurred while parsing: {e}")
            traceback.print_exc()

            return

        self.handlers.sort(key=get_id)

        return

    def handler(self, payload):

        # SS handel method, find suitable handler and run it
        # Ran inside of a ThreadPoolExecutor

        try:

            sock = payload['sock']
            data = payload['data']

            if data['id'] > len(self.handlers) or data['id'] < 0:

                # No handler found, lets exit:

                self.log.warning("No handler found for ID [{}]! Dropping packet...".format(data['id']))

                return

            hand = self.handlers[data['id']]
            uuid = data['uuid']
            req_id = data['id']
            content = data['content']

            self.log.info("Received {} from {} ".format(data, sock))

            if uuid is None and sock.device_uuid is None and req_id == 1:

                # Device is attempting to authenticate

                hand.handel_server(sock, content)

                return

            # Getting device here:

            device = self.devices.get_by_uuid(uuid)

            if device is None or sock.device_uuid != device.uuid:

                # Device is not authenticated,
                # OR an authentication error has occurred.
                # Ignoring packet.

                self.log.warning("Device not authenticated! Dropping packet...")

                return

            hand.handel_server(device, content)

        except Exception as e:

            self.log.warning("Error occurred during handler thread: {}".format(e))


class SocketClient:

    def __init__(self, chas, host, port):

        self.chas = chas  # CHAS Instance
        self.running = False  # Value determining if the Socket Client is running
        self.connected = False  # Value determining if we are connected to the server
        self.host = host  # Hostname of the CHAS server
        self.port = port  # Port num of the CHAS server
        self.sel = selectors.DefaultSelector()
        self.sock = None  # CHAS socket connected to the CHAS server
        self.handlers = []  # List of ID handlers
        self.thread = None  # Threading object

        self.log = get_logger("CORE:NET")

    def start(self):

        # Function for starting the Socket Client

        self.running = True

        self.log.debug("Parsing and loading handlers...")

        self.parse_handlers()

        self.log.debug("Starting listen thread...")

        self.thread = threading.Thread(target=self._sc_event_loop)
        self.thread.daemon = True
        self.thread.start()

        return

    def stop(self):

        self.running = False

        # Iterate over handlers to stop them:

        for hand in self.handlers:

            # Stop the handler:

            hand.stop()

        self.thread.join()

    def _start_connection(self):

        addr = (self.host, self.port)

        self.log.debug("Establishing connection to CHAS server {}:{}".format(addr[0], addr[1]))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 10000)

        self.sock.connect_ex(addr)

        self.sock.setblocking(False)

        events = selectors.EVENT_READ
        message = CHASocket(self.sel, self.sock, addr, self.log)
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

        self.log.debug("Loaded [{}] network handlers!".format(len(self.handlers)))

        return

    def _sc_event_loop(self):

        self._start_connection()

        while self.running:

            events = self.sel.select(timeout=5)

            for key, mask in events:

                message = key.data

                try:

                    if mask & selectors.EVENT_READ:

                        data = message.read()

                        if data is None:

                            continue

                        self.handler(data, message)

                except Exception as e:

                    self.log.error("Error during event loop: {}!".format(e))
                    self.log.error("Removing socket [{}:{}]".format(self.host, self.port))
                    message.close()

                    raise e

            if not self.sel.get_map():

                pass

    def handler(self, data, sock):

        try:

            req_id = data['id']
            content = data['content']
            hand = self.handlers[req_id]
            server = self.chas.server

            self.log.info("Received data {}".format(data))

            if req_id == 1:

                # Authenticating...

                hand.handle_client(sock, content)

                return

            hand.handle_client(server, content)

        except Exception as e:

            self.log.warn("Error occurred during handle method: {}".format(e))
