"""
Input modules for the output handler.

An input module is any iterable that returns float information when sampled.
Inputs are iterables, or generators, that are iterated when sampled.
These generators can have an end, or they could iterate indefinitely.

Input modules can be chained together,
so that they can effect each other.

We primarily provide support for reading musical files,
and getting information from a network stream,
as this is the most relevant operation at this time.
"""

import pathlib
import wave

from chaslib.sound.convert import Int8, Int16, Int32, Float32, NullConvert, BaseConvert
from chaslib.sound.utils import BaseModule


class BaseInput(BaseModule):

    """
    BaseInput - Class all child inputs should inherit!

    Inputs should READ audio information from somewhere,
    be it a stream, file, stdin, ect,
    and this information we read should be bytes.
    Therefore, we should return FRAMES of audio
    in the 'get_next()' function, and we will handle the process of conversion.

    We offer some basic functionality, such as providing an iterable interface for sampling,
    and the automatic conversion of bytes into floats,
    very similar to how BaseModule operates.
    If the length of the audio is reported(Number of audio frames),
    then we will automatically stop this audio instance once we reach that point.
    Otherwise, we will continue to sample until we come across non-byte objects,
    or the input module stops itself.

    We also offer methods for repeating,
    meaning that this audio file will repeat once we reach the end.
    If this is not possible, i.e we are a network stream,
    then you can disable all repeats by setting 'allow_repeat' to False.

    If audio is single channel,
    then we will only return one value.
    If it is stereo, then we will return two inputs for each frame,
    the first being the left channel and the second being the right channel.
    """

    def __init__(self) -> None:
        
        super().__init__()

        self.convert = NullConvert()  # Converter instance

        self.final_bit = None  # Final bit of audio before sending 
        self.length = None  # Length of the audio information
        self.loop = False  # Value determining if we should repeat
        self.allow_repeat = True  # Value determining if we should allow repeats

    def bind_converter(self, conv):

        """
        Binds a converter to this input module.

        The converter MUST inherit BaseConvert,
        or else and excpetion will be raised.

        :param conv: Converter to bind to this input module
        :type conv: BaseConvert
        """

        # Check if conv inherits BaseConverter:

        assert isinstance(conv, BaseConvert), "Converter MUST inherit BaseConvert!"

        # Add the converter:

        self.convert = conv

    def repeat(self):

        """
        Function called when we are requested to repeat.

        This only occurs if the following conditions are met:

            - We are set to repeat by the player
            - The module has not explicitly disabled repeating
            - The end of our audio is reached - determined by audio length

        If none of these parameters are met,
        then we will not repeat.

        The module should put repeat code in here to reset the audio stream back to zero.
        When invoked automatically, we will also reset the index to zero.
        """ 

        pass

    def nframes(self, frames):

        """
        Sets the length of the audio information we are reading.

        This is the number of frames in the audio.

        This allows us to determine when the audio is complete,
        so we can do things like repeat or automatically stop gracefully.

        Features like repeat will not be used if this value is not provided!
        """

        if frames < 1:

            raise ValueError("Invalid audio legnth! Must be greater than 0!")

        self.length = frames

    def format_from_width(self, width):

        """
        Binds the necessary converter based upon the width of a sample.
        """

        if width == 1:

            # Int8:

            self.bind_converter(Int8())

        if width == 2:

            # Int16:

            self.bind_converter(Int16())

        if width == 4:

            # Int32

            self.bind_converter(Int32())

    def __next__(self):

        """
        Gets the next value in this module and returns is.

        We call 'get_next()' to get this value,
        and then increase the index of this module.

        We also check if we should exit or repeat,
        stopping ourselves or restarting as necessary.

        :return: Next value
        :rtype: float
        """

        # Check if we need to stop:

        if self.length is not None and self.index == self.length - 1:

            # Check if we should repeat on the next frame:

            if self.allow_repeat and self.loop:

                # Repeat this audio instance:

                self.repeat()
                self.index = 0

            else:

                # Otherwise, lets exit:

                self.info.running = False

                return

        if self.final_bit:

            # Revert the value:

            final = self.convert.revert(self.final_bit)

            # Overide the final bit

            self.final_bit = None

            # Return the final value

            return final

        val = self.get_next()

        if type(val) != bytes:

            # We must work with bytes! Lets exit, as we are probably done:

            self.info.running = False

            return 0

        # Split val in half:

        split = [val[:self.convert.width], val[self.convert.width:]]

        if len(split) > 1:

            # Save our final bit:

            self.final_bit = split[1]

        # Increment our index:

        self.index += 1

        return self.convert.revert(split[0])


class WaveReader(BaseInput):

    """
    Reads audio information from a wave file.

    We automatically add the correct converter based upon the sample width,
    and figure out how many channels we have.

    We only support stereo and mono files.
    Anything more we will not play!

    :param path: Path to the wave file
    :type path: str
    """

    def __init__(self, path) -> None:

        super().__init__()

        self.path = self.path = str(pathlib.Path(path).resolve())
        self.wave = None  # Wave file instance

    def start(self):

        """
        Starts this module,
        we load the wave file, and get relevant information from it.
        """

        # Load the wave file:

        self.wave = wave.open(self.path, 'rb')

        # Set the number of channels:

        self.info.channels = self.wave.getnchannels()

        # Set the length of the wave file:

        self.nframes(self.wave.getnframes())

        # Configure the converter:

        self.format_from_width(self.wave.getsampwidth())

    def stop(self):

        """
        Stops this module,
        we stop the wave reader.
        """

        self.wave.close()

    def repeat(self):

        """
        Restarts the wave file instance.
        """

        self.wave.rewind()

    def get_next(self):

        """
        Gets the next frame in the wave file and returns it.
        """

        # Get and return:

        return self.wave.readframes(1)
