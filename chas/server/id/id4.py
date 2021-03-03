# ID Handler for network audio streaming

from id.idhandle import IDHandle
from chaslib.sound.out import NetModule
from chaslib.sound.input import NetReader


class AudioStream(IDHandle):

    def __init__(self):

        super(AudioStream, self).__init__('Audio Streamer',
                                          'Handler for audio streaming',
                                          4)

        self.stream = None  # Instance of our stream
        self.chunk = 0  # Chunksize of data to read

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

    def stop(self):

        """
        Called when we are removed from the networking component.

        This might occur if the instance does not want audio streaming enabled.

        We stop and remove the NetReader from the OutputHandler and quit.
        """

        # Stop the NetReader:

        self._stop_stream()

    def _read_stream(self, data):

        """
        Send the given audio information to the NetReader.

        We let the NetReader do all the decoding and conversion.
        """

        self.stream.put(data)

    def _start_stream(self, data):

        """
        We start the audio stream on the client.

        This simply means we create and add an NetReader module to the OutputHandler.
        We will then procede to pass audio information to them.
        """

        # Create and add the NetReader:

        self.log.debug("Starting audio stream...")

        self.stream = self.chas.sound.bind_synth(NetReader())

    def _stop_stream(self):

        # Method for starting and configuring audio stream

        self.log.debug("Stopping audio stream...")

        self.stream.stop()
