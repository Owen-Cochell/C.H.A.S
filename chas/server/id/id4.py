# ID Handler for network audio streaming

from id.idhandle import IDHandle
from chaslib.soundtools import RawAudio
import base64


class AudioStream(IDHandle):

    def __init__(self):

        super(AudioStream, self).__init__('Audio Streamer(Client)',
                                          'Handler for audio streaming',
                                          4)
        self.stream = None  # Instance of our stream
        self.chunk = 0  # Chunksize of data to read
        self.min_buff = 3  # How big the buffer should be before we play, to prevent skips

    def handel_client(self, dev, data):

        id_num = data['id']
        contents = data['data']

        if id_num == 0:

            # Server wants to start an audio stream:

            self._start_stream(contents)

            return

        if id_num == 1:

            # Server sent us some audio data:

            self._read_stream(contents)

        if id_num == 2:

            # Server wants to stop audio stream

            self._stop_stream()

    def _read_stream(self, data):

        # Read from audio stream

        #print(f"Writing audio data: {data}")

        self.stream.write(base64.b64decode(data))

    def _start_stream(self, data):

        # Method for starting and configuring audio stream

        self.chunk = data['chunk']

        self.stream = RawAudio(

            self.chas,
            form=data['format'],
            channels=data['channels'],
            rate=data['rate'],
            chunk=self.chunk,
            min_buff=self.min_buff,
            size=data['size'],
            stream=False
        )

        self.stream._start()

        return

    def _stop_stream(self):

        # Method for starting and configuring audio stream

        print("Stopping stream...")

        self.chunk = 0
        self.stream.stop()

        return
