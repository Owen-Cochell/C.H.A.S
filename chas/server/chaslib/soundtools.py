#!/usr/bin/python

# This file will handle everything to do with sound

import speech_recognition as sr
import pyaudio
import subprocess
import os
from threading import Thread, ThreadError, Event
from base64 import b64encode
import wave
from math import ceil

from chaslib.sound.input import WaveReader
from chaslib.misctools import get_logger

class Listener:

    """
    CHAS Listener class
    Manages Microphone and Recognizer classes
    Maintains an internal state of weather it's listening or not, to prevent "Dual Listening"
    """

    def __init__(self, word, chas):
        
        """
        Constructor for the listener class
        """

        self.chas = chas   # Instance of the CHAS masterclass
        self.word = word  # CHAS Wakeword
        self.rec = sr.Recognizer()  # Speech recognizer for speech recognition
        self.mic = sr.Microphone()  # TODO: Setup microphone selection
        self.wake = Event()  # Event determining if we have a wake word event
        self.pause = Event()  # Event determining if we are paused(True means we are not paused
        self.sphinx = True  # Boolean determining if we recognize with the offline engine

        self.log = get_logger()

        self.pause.set()
        self.wake.clear()

    def listen(self, timeout=None):

        """
        Function for listening to default mic
        :return: String of words recognized
        """

        # Waiting for instance to be unpaused

        self.log.debug("Listening for user input...")

        val = self.pause.wait(timeout=timeout)

        if not val:

            # We timed out, return nothing

            return ''

        # Setting value to not clear

        self.pause.clear()

        with self.mic as mic:

            # Adjusting for ambient noise

            self.rec.adjust_for_ambient_noise(mic)

            # PLaying notification sound

            #WavePlayer(self.chas, path=os.path.join(self.chas.settings.media_dir, 'sounds/listen.wav')).start()

            # Add a WaveReader to OutputHandler:

            player = self.chas.sound.bind_synth(WaveReader(os.path.join(self.chas.settings.media_dir, 'sounds/listen.wav')))
            player.start()
            player.join()

            # Listening for voice

            audio = self.rec.listen(mic)

        if self.sphinx:

            # Recognize with the offline pocketsphinx engine

            self.log.debug("Recognizing via sphinx...")

            value = self._recognize_sphinx(audio)

        else:

            self.log.debug("Recognizing via google...")

            value = self._recognize_google(audio)

        # We are done listening, so unpause

        self.pause.set()

        return value

    def continue_listen(self):

        """
        Continuously listening until wake word is heard
        """

        self.log.debug("Recognizing in the background...")

        # Checking for pause status:

        self.pause.wait()

        # Starting background listen and getting stop method

        stop = self.rec.listen_in_background(self.mic, self._cont_call)

        # Waiting until wake word is detected

        self.wake.wait()

        # Stopping background listen

        stop()

        # Clearing the wakeword parameter

        self.wake.clear()

        return True

    def _cont_call(self, rec, audio):

        """
        Backend function for handling continuous callbacks
        :param rec: Recognizer instance(Unneeded, discarded)
        :param audio: Audio instance to recognize
        """

        # Checking if we are paused:

        if not self.pause.isSet():

            # Paused, waiting and ignoring audio data

            self.pause.wait()

            return

        # Waiting if we are paused

        self.pause.wait()

        # Recognizing audio with Pocketshpinx

        try:

            word = self._recognize_sphinx(audio)

            self.log.debug("Recognized word: {}".format(word))

        except Exception as e:

            # Failed to recognize, return from callback

            self.log.debug("Failed to recognize: {}".format(e))

            return

        # Checking if our wakeword is in the list

        if self.word in word:

            # Found our wake word:

            self.wake.set()

            self.log.debug("Found our wakeword: {}".format(self.word))

            return

        # No wake up word

        return

    def _recognize_sphinx(self, audio):

        """
        Function for recognizing audio with PocketSphinx, an offline engine
        :param audio:
        :return:
        """

        try:

            # Attempting to recognize with PocketSphinx

            words = self.rec.recognize_sphinx(audio)

        except sr.UnknownValueError:

            # Unknown Value error, returning nothing

            raise Exception("Unknown Value Error")

        return words

    def _recognize_google(self, audio):

        """
        Function for recognizing audio with the Google API
        :param audio: Audio data to be recognized
        :return:
        """

        try:

            words = self.rec.recognize_google(audio)

        except sr.UnknownValueError:

            # Unknown value raising exception

            raise Exception("Unknown Value - unable to Recognise")

        except sr.RequestError:

            # Request error while handling, switching over to pocketsphinx mode

            # TODO: Add internet connectivity test

            self.sphinx = True

            raise Exception("Request Error - unable to communicate with remote services")

        return words


class RawAudio(object):

    # Class for reading and writing audio streams

    def __init__(self, chas, form=None, channels=1, rate=48000, chunk=1024, dev=None, stream=False, min_buff=0, size=0):

        self.queue = []  # Queue of data to write
        self.playing = False  # Boolean value determining if we are playing
        self.done = False  # Value determining if we should stop when queue is empty
        self.form = form  # Format of audio data
        self.channels = channels  # number of channels in audio data
        self.rate = rate  # Rate of audio data
        self.chunk = chunk  # Chunksize
        self.p = pyaudio.PyAudio()  # Pyaudio instance
        self.stream = None  # Pyaudio stream
        self.thread = None  # Thread of audio consumer
        self.net = stream  # Boolean value determining if we should stream audio data to clients
        self.net_stream = None  # Network Streamer instance
        self.min_buff = min_buff  # How many audio writes must be in the buffer until audio is written
        self.size = size  # Size of audio data until we gracefully shut down
        self.iter = 1  # Writes we must do to reach to maxsize
        self.chas = chas  # CHAS Instance

        if dev is None:

            self.dev = self.p.get_default_output_device_info()['index']

        else:

            self.dev = dev

    def write(self, data):

        # Write data to the queue

        self.queue.append(data)

        return

    def _write(self, data):

        # Write data to the audio stream

        #print(f"Writing data: {data}")
        self.stream.write(data)

        return

    def _audio_consumer(self):

        # Audio consumer

        num = 0

        while self.playing:

            if not self.queue and not self.done and self.playing:

                # Buffer control: Wait until buffer has specified chunks before writing:

                while len(self.queue) < self.min_buff and self.playing:

                    # Wait until min biff is reached:

                    continue

            if self.queue:

                # Read audio data:

                #print(self.queue)

                data = self.queue.pop(0)

                self._write(data)

                if self.net:

                    self.net_stream.write(data)

                num = num + 1

                if num >= self.iter:

                    self.playing = False

                    self.queue = []

                    self.stream.stop_stream()
                    self.stream.close()

                    self.p.terminate()

                    return

                continue

            elif self.done:

                # Queue is empty, and we must finish:

                return

        return 

    def _start(self):

        # Method for starting stream and thread:

        self.stream = self.p.open(

            format=self.form,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
        )

        if self.net:

            self.net_stream = NetAudio(

                self.form,
                self.channels,
                self.rate,
                self.chas,
                chunk=self.chunk,
                size=self.size
            )

        self.playing = True

        if self.size != 0:

            # Calculate how many iterations we must do to reach the end:

            self.iter = ceil(self.size / self.chunk)

        self.thread = Thread(target=self._audio_consumer)
        self.thread.start()

    def wait(self):

        # Wait until the queue is played/buffer limit reached,
        # and netstream is done, then return

        if self.size is not 0:

            self.thread.join()

        else:

            # Wait until buffer is empty:

            self.done = True

            self.thread.join()

        if self.net:

            # Waiting for network streamer to finish, IA:

            self.net_stream.wait()

        return

    def _stop(self):

        # Stopping processes pertaining to this object only.

        if not self.playing:

            return

        self.playing = False

        self.queue = []

        self.thread.join()

        self.stream.stop_stream()
        self.stream.close()

        self.p.terminate()

    def stop(self):

        self._stop()

        if self.net:
            
            self.net_stream.stop()


class WavePlayer(RawAudio):

    # Class that plays Wave files

    def __init__(self, chas, path=None, chunk=1024, dev=None, net=False):

        self.chas = chas  # CHAS Instance
        self.path = path  # Path to Wave file
        self.wf = wave.open(self.path, 'rb')  # Wave file object
        self.chunk = chunk  # Chunksize
        self.wf_thread = None  # Thread object
        self.wf_play = False  # Boolean determining if we are playing audio
        self.done = False  # Boolean determining if we are done reading WAV data
        self.wf_p = pyaudio.PyAudio()
        self.net = net  # Boolean value determining if we should stream audio to clients
        super(WavePlayer, self).__init__(self.chas,
                                         form=self.wf_p.get_format_from_width(self.wf.getsampwidth()),
                                         channels=self.wf.getnchannels(),
                                         rate=self.wf.getframerate(),
                                         dev=dev,
                                         stream=self.net,
                                         size=self.wf.getnframes()
                                         )

    def _wav_write(self):
        
        # Function for writing WAV data to stream:

        data = self.wf.readframes(self.chunk)

        while data != b'' and self.wf_play:

            super().write(data)

            data = self.wf.readframes(self.chunk)

        # All WAV data written, stopping object

        super().wait()
        self.stop()

        return

    def block(self):

        # Blocks execution until the file has stopped playing

        self.thread.join()

        return

    def start(self):

        # Function for starting Wave file player

        super()._start()
        self.wf_play = True
        self.done = False
        self.wf_thread = Thread(target=self._wav_write)
        self.wf_thread.start()

    def stop(self):

        # Function for stopping WAV playing

        if not self.wf_play:

            return

        self.wf_play = False

        self.wf_thread = None
        self.wf.close()
        self.done = True
        self.wf_play = False
        super().stop()

    def is_playing(self):

        """
        Method that determines if we are playing or not
        :return: Returns boolean value determing if we are playing
        """

        return self.playing


class NetAudio:

    # Class for streaming audio to clients

    def __init__(self, form, channels, rate, chas, chunk=1024, size=0):

        self.chas = chas  # CHAS Masterclass
        self.queue = []  # Queue of data to write
        self.playing = False  # Boolean determining if we are sending audio
        self.done = False  # Boolean determining if we quit on empty queue
        self.format = form  # Format of audio data
        self.channels = channels  # Audio channels
        self.rate = rate  # Frames per buffer
        self.chunk = chunk  # Chunk size
        self.thread = None  # Consumer thread
        self.size = size  # Size of the total audio payload
        self.iter = 1  # How many iterations we must do until end of file

        self.start()

    def _gen_starter_payload(self):

        return {'id': 0, 'data': {'format': self.format, 'channels': self.channels, 'rate': self.rate, 'chunk': self.chunk, 'size': self.size}}

    def _gen_data_payload(self, data):

        b64_bytes = b64encode(data)

        b64_string = b64_bytes.decode('utf-8')

        return {'id': 1, 'data': b64_string}

    def _gen_stop_payload(self):

        return {'id': 2, 'data': None}

    def start(self):

        # Method for starting the streamer

        self.playing = True

        if self.size is not 0:

            # Calculate how many iterations we must do to reach the end:

            self.iter = ceil(self.size / self.chunk)
 
        self._write(self._gen_starter_payload())

        self.thread = Thread(target=self._event_loop)
        self.thread.start()

        return

    def wait(self):

        # Wait for network streamer to finish, and all clients have finished reading/writing

        if self.size is not 0:

            self.thread.join()

        else:

            self.done = True
            self.thread.join()

        return

    def _stop(self):

        # Stopping functions specific to this instance, not clients

        if not self.playing:

            # Already stopped

            return

        self.playing = False

    def stop(self):
        
        # Method for stopping the streamer

        self._stop()

        self._write(self._gen_stop_payload())

    def write(self, data):
        
        # Method for adding audio data to the queue

        self.queue.append(data)

        return

    def _event_loop(self):

        # Simple consumer method: Sends audio data to devices

        num = 1

        while self.playing:

            if self.queue:

                self._write(self._gen_data_payload(self.queue[0]))
                self.queue.pop(0)

                num = num + 1

                if num >= self.iter:

                    # Stops audio streams on our end, but not on client

                    self._stop()

                    return

            elif self.done:

                # queue is empty and we need to stop playing:

                return

            continue

        return

    def _write(self, data):
        
        # Writes the data to all devices

        for dev in self.chas.devices:
            
            dev.send(data, 4)

        return


class Speaker:

    def __init__(self):

        self.rate = 175
        self.pitch = 50
        self.voice = 'default'
        self.amplitude = 100
        self.voices = []
        self.location = None

    def get_voices(self):

        if self.location is None:

            # No data location.

            self.get_data_location()

        # Changing directory to voice files:

        master_data = {}

        for root, dirs, files in os.walk(os.path.join(self.location, "voices/")):

            index = root.find('/voices/')

            current_dir = root[index+8:]

            if current_dir == '':

                current_dir = 'main'

            dir_data = {}

            for i in files:

                file = open(os.path.join(root, i), 'r')
                lines = file.readlines()

                lang = []
                name = None
                gender = None

                for line in lines:

                    line = line.rstrip()

                    if line.find('name') != -1:

                        name = line[5:]
                        continue

                    if line.find('language') != -1:

                        lang.append(line[9:])
                        continue

                    if line.find('gender') != -1:

                        gender = line[7:]
                        continue

                file.close()

                data = {'gender': gender, 'lang': lang}

                dir_data[name] = data

            master_data[current_dir] = dir_data

        self.voices = master_data

        return

    def get_data_location(self):

        # Getting location of espeak directory:

        process = subprocess.Popen(['espeak', '--version'], stdout=subprocess.PIPE)

        try:

            out = process.communicate()[0].decode('utf-8')

        except:

            print("An error occurred!")
            empty = input("Press enter to continue...")

        # Extracting data location:

        index = out.index('Data at: ')

        location = out[index+9:]

        self.location = location.rstrip()

        return

    def add(self, mesg, output=""):

        """
        Compatibility function,
        Allows for easy output of given info
        """

        self.speak(mesg)

    def speak(self, mesg):

        # Function for speaking text:

        process = subprocess.Popen(['espeak', '-a', str(self.amplitude), '-p', str(self.pitch), '-s', str(self.rate), '-v', str(self.voice), str(mesg)],
                                   stderr=subprocess.PIPE)

        error = process.communicate()[0]
        rc = process.returncode

        if rc != 0:

            print("An error occurred:")
            print(rc)
            print(error)
            empty = input("Press enter to continue...")
            return

        return
