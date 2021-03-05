# A class for handling devices

import uuid
import queue

# TODO: Add ping, test for socketserver discrepancies, ...


class Device:

    def __init__(self, chas, name, ip, port, sck):

        self.chas = chas  # CHAS Masterclass instance
        self.name = name  # Name of our device(User Defined)
        self.ip = ip  # IP Address of our device(User Defined)
        self.port = port  # Port of our device
        self.uuid = None  # Unique device ID
        self.sock = sck  # CHAS Socket
        self.auth = False  # Value determining if this device is authenticated
        self.queue = []  # Queue for special handling

    def send(self, content, id_num, encoding='utf-8'):

        # Function for sending data to remote device

        data = {'id': id_num,
                'uuid': self.uuid,
                'content': content}

        #self.chas.net.write(data, self.uuid)

        self.sock.write(data)

    def get(self, content, id_num, encoding='utf-8'):

        # Function for getting raw data from CHAS server, bypassing server-side handlers

        content_uuid = str(uuid.uuid4())

        inner_data = {'content-uuid': content_uuid,
                      'content-status': 0,
                      'content-id': id_num,
                      'content-type': 0,
                      'content': content}

        data = {'id': 3,
                'uuid': self.uuid,
                'content': inner_data}

        self.chas.net.write(data)

        while True:

            for i in self.queue:

                if i['content-uuid'] == content_uuid:

                    # Found our request:

                    message = i['content']

                    self.queue.remove(i)

                    return message

    def add_queue(self, data):

        self.queue.append(data)


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


class Devices:

    """
    Class that maintains a list of devices connected to the server
    Allows for many CHAS operations on said devices
    """

    def __init__(self, chas):

        self.chas = chas  # CHAS Mastercalss instance
        self.__devs = []  # List of all device objects, None will always be the first value

    def register(self, dev, auth=True):

        # Register a device object with the list
        # 'Auth' specifies if we want to authenticate the device
        if auth:

            self.__authenticate(dev)

        self.__devs.append(dev)

    def create(self, name, ip, port, sock):

        # Create new device object with the given information, and register it

        dev = Device(self.chas, name, ip, port, sock)

        self.__authenticate(dev)

        self.__devs.append(dev)

        return

    def __authenticate(self, dev):

        # Authenticate a given device

        # Assigning device UUID

        dev.uuid = str(uuid.uuid4())
        dev.auth = True

        # Binding socket to device

        dev.sock.bind(dev.uuid)

    def __deauthenticate(self, dev):

        # De-authenticate a given device

        # Changing device authentication status

        dev.auth = False

        # Removing UUID

        dev.uuid = None

    def get_by_uuid(self, uid):

        # Get device instance by UUID

        dev_ind = next((dev for dev, dev in enumerate(self.__devs) if dev.uuid == uid), None)

        if dev_ind is None:

            return None

        return dev_ind

    def get_by_name(self, name):

        # Get device instance by name, UUID method is preferred.

        dev_ind = next((dev for dev, dev in enumerate(self.__devs) if dev.name == name), None)

        if dev_ind is None:

            return None

        return self.__devs[dev_ind]

    def unregister_by_uuid(self, uid):

        # Unregister device by UUID

        dev = self.get_by_uuid(uid)

        self.__unregister(dev)

    def unregister_by_name(self, name):

        # Unregister device by name

        dev = self.get_by_name(name)

        self.__unregister(dev)

    def __unregister(self, dev):

        # Unregister device by device instance, backend for unregistering devices

        self.__deauthenticate(dev)

        self.__devs.remove(dev)

    def get_device_info(self):

        # Returns Dictionary of all devices and their information

        info = []

        for dev in self.__devs:

            # Getting device info here:

            innerdata = {'deviceName': dev.name, 'deviceIP': dev.ip, 'devicePort': dev.ip, 'deviceID': dev.uuid}

            info.append(innerdata)
            
        return info

    def __len__(self):

        """
        Adding len support for devices class
        :return:
        """

        return len(self.__devs)

    def __getitem__(self, position):

        """
        Dunder method to support getting device by index
        :param position: Index of device to get
        :return: Device instance
        """

        return self.__devs[position]