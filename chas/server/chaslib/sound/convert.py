"""
Tools for converting byte information to floats, and vice versa.

Because our effect modules expect audio information in floats, 
we use converters to convert these values back and forth for manipulation,
and output.

We may have to do some crazy stuff for audio format normalization,
as in an ideal world we will be working with floats.
"""

import struct


class BaseConvert(object):

    """
    Base converter class - All child converts should inherit!

    A converter allows for automatic, under-the-hood conversion of audio information.
    Output modules and input modules can attach converters to convert or revert audio information.

    We only provide the basic framework for converters, and allow for automatic struct creation.
    """

    def __init__(self):

        self.char = ''  # Character used in the struct converter
        self.struct = None  # struct instance to use for conversion
        self.byte_order = '<'  # Specifies the byte order, defaults to little-endian
        self.width = 0  # Width of the converter - size of the bytes returned

    def big_endian(self):
        """
        Changes the byte order to big endian.
        This only takes effect before the struct instance is created,
        so be sure to call this before 'gen_struct()'!
        """

        # Chnage the byte char:

        self.byte_order = '>'

    def gen_struct(self, char):

        """
        Creates a struct instance using the given char

        :param char: Character to use for struct
        :type char: str
        """

        self.char = char

        # Generate the struct instance:

        self.struct = struct.Struct(self.byte_order + self.char)

    def convert(self, inp):

        """
        Convert function - Converts floats into usable bytes for output.

        You can safely assume that the input will be signed floats.
        Ideally, the converter should return bytes.

        :param inp: Float to convert
        :type inp: float
        :return: COnverted bytes of the float
        :rtype: bytes
        """

        raise NotImplementedError("Should be implemented in child class!")


    def revert(self, inp):
        """
        Revert function - Reverts bytes into floats.

        You can safely assume that the input will be signed floats.
        Ideally, this function should return floats

        :param inp: Bytes to convert into floats
        :type inp: bytes
        :return: Float representing the bytes
        :rtype: float
        """

        raise NotImplementedError("Should be implemented in child class!")


class NullConvert(BaseConvert):

    """
    Just like the name - We simply return what we were given!
    """

    def __init__(self):
        super().__init__()

        self.width = 1  # Set our width

    def convert(self, inp):
        
        """
        Return exactly what we were given

        :return: Float input
        :rtype: float
        """

        return inp

    def revert(self, inp):
        
        """
        Return exactly what we were given

        :return: Bytes input
        :rtype: bytes
        """

        if type(inp) in [list, tuple]:

            # Return the 0 index:

            return inp[0]

        return inp


class Float32(BaseConvert):

    """
    Float converter - Converts data into floats and vice versa.
    """

    def __init__(self):

        super().__init__()

        # Configure the struct instance:

        self.gen_struct('f')

        self.width = 4  # Set our width

    def convert(self, inp):
        """
        Converts the given float into bytes

        :param inp: Float to convert
        :type inp: float
        :return: Converted float
        :rtype: bytes
        """

        # Convert and return:

        return self.struct.pack(inp)

    def revert(self, inp):
        """
        Reverts the given bytes into floats.

        :param inp: Bytes to revert into floats
        :type inp: bytes
        :return: Reverted bytes
        :rtype: float
        """
        
        # Convert and return:

        return self.struct.unpack(inp)[0]


class Int8(BaseConvert):

    """
    Int8 converter - Converts floats into Int8 and vice versa
    """

    def __init__(self):

        super().__init__()

        self.gen_struct('b')

        self.width = 1  # Set our width

    def convert(self, inp):
        
        """
        Converts the given float into Int8 bytes

        :return: Converted bytes
        :rtype: bytes
        """

        # Convert and return:

        return self.struct.pack(int(inp * 127))

    def revert(self, inp):

        """
        Reverts the given bytes into Int8

        :return: Converted ints
        :rtype: int
        """

        # Convert and return

        return float(self.struct.unpack(inp)[0] / 127)


class Int16(BaseConvert):

    """
    Int16 converter - For ints between -32768-32767
    """

    def __init__(self) -> None:
        
        super().__init__()

        # Configure the struct instance:

        self.gen_struct('h')

        self.width = 2  # Set our width

    def convert(self, inp):

        """
        Converts the given floats into int16 bytes.

        :param inp: Float to convert
        :type inp: float
        :return: COnverted float
        :rtype: bytes
        """

        # Convert and return:

        return self.struct.pack(int(inp * 32767))

    def revert(self, inp):
        
        """
        Reverts the given bytes into floats.

        :param inp: Bytes to convert
        :type inp: bytes
        :return: Converted bytes
        :rtype: bytes
        """

        # Convert the bytes and return:

        return float(self.struct.unpack(inp)[0] / 32767)


class Int32(BaseConvert):

    """
    Int32 - Convert data into int32 and vice versa
    """

    def __init__(self):

        super().__init__()

        # Generate our struct instance:

        self.gen_struct("i")

        self.width = 4  # Configure our width

    def convert(self, inp):

        """
        Converts the given float into bytes

        :param inp: Float to convert
        :type inp: float
        :return: Float in byte format
        :rtype: bytes
        """

        # Convert and return:

        return self.struct.pack(int(inp * 2147483647))

    def revert(self, inp):

        """
        Converts the given bytes into floats

        :param inp: Bytes to convert
        :type inp: bytes
        :return: Bytes in float format
        :rtype: float
        """

        # Convert and return:

        return float(self.struct.unpack(inp)[0] / 2147483647)
