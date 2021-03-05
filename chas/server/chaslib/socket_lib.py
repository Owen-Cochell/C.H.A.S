import io
import json
import struct
import sys
import socket

"""
A CHAS implementation of the Python Socket.
The CHAS socket handles all low-level read/write operations,
And includes support for CHAS device objects.
"""


class CHASocket:

    def __init__(self, selector, sock, addr, log):

        self.sel = selector  # Selector object
        self.sock = sock  # Socket object
        self.addr = addr  # Address of client
        self._jsonheader_len = None  # Length of JSON header
        self._jsonheader = None  # Decoded JSON header
        self.content = None  # Decoded content of the response
        self.__dev = None  # UUID of device socket is binded to, allows for high level CHAS socket management

        self.log = log

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32000)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32000)
        self.sock.settimeout(5)

    def _read(self, byts):

        # Read a specified amount of bytes

        data = b''
        orig = int(byts)

        while True:

            try:

                data = data + self.sock.recv(byts)

            except BlockingIOError:

                # Resource temporarily unavailable!

                self.log.info("Socket temporarily unavailable!")

            finally:

                # Check how many bytes we have read - Prevents Socket Drift:

                byts = orig - len(data)

                if len(data) == orig:

                    # We are done lets break:

                    break

        return data

    def read(self):

        if self._jsonheader_len is None:

            self._process_proto_header()

        if self._jsonheader_len is not None:

            if self._jsonheader is None:

                self._process_jsonheader()

        if self._jsonheader:

            if self.content is None:

                return self._process_request()

        self._read(50)

        return None

    def _write(self, content_bytes):

        # Write data to the stream

        self.sock.sendall(content_bytes)

        return

    def write(self, content, encoding='utf-8'):

        # Encoding data and sending data

        encoded = self._json_encode(content)

        message = self._create_message(encoded, 'text', encoding)

        self._write(message)

    def _json_encode(self, mesg, encoding="utf-8"):

        # Encode message in JSON

        return json.dumps(mesg, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding="utf-8"):

        # Decode message in JSON

        try:

            tiow = io.TextIOWrapper(
                io.BytesIO(json_bytes), encoding=encoding, newline=""
            )

            obj = json.load(tiow)
            tiow.close()

            return obj

        except Exception as e:

            self.log.error("Error while decoding: {}".format(json_bytes))

    def _process_proto_header(self):

        # Method for processing proto header

        hdrlen = 2

        content = self._read(2)

        if len(content) == hdrlen:

            self._jsonheader_len = struct.unpack(
                ">H", content
            )[0]

            return

    def _process_jsonheader(self):

        hdrlen = self._jsonheader_len

        content = self._read(hdrlen)

        if len(content) == hdrlen:

            self._jsonheader = self._json_decode(
                content, encoding="utf-8"
            )

            for reqhd in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):

                if reqhd not in self._jsonheader:

                    raise Exception("Malformed JSON Header!")

        return

    def _process_request(self):

        # Method for processing the request

        content_len = self._jsonheader["content-length"]

        contents = self._read(content_len)

        encoding = self._jsonheader["content-encoding"]

        content = self._json_decode(contents, encoding=encoding)

        self._jsonheader = None
        self._jsonheader_len = None

        return content

    def _create_message(self, content_bytes, content_type, content_encoding):

        # Method for creating message:

        header = {"byteorder": sys.byteorder,
                  "content-type": content_type,
                  "content-encoding": content_encoding,
                  "content-length": len(content_bytes)}

        header_bytes = self._json_encode(header)

        proto_header = struct.pack(">H", len(header_bytes))

        message = proto_header + header_bytes + content_bytes

        return message

    @property
    def device_uuid(self):
        
        return self.__dev

    def bind(self, uuid):

        # Binds a device UUID to the socket, ensures CHAS Socket security,
        # And allows for higher level CHAS socket operations.
        # This action is permanent for all CHAS socket instances.

        if self.__dev is not None:

            # Ignoring attempted binding attempt, already binded

            return

        self.__dev = uuid
        
        return

    def close(self):

        # Method for closing the websocket

        print(f"Closing connection to: {self.addr}")

        try:

            self.sel.unregister(self.sock)

        except Exception as e:

            print(f"Error unregistering socket: {e}")

        try:

            self.sock.close()

        except Exception as e:

            print(f"Error closing socket: {e}")

        finally:

            self.sock = None
