"""
General utilities for sound processing
"""


import time

from collections import deque


def get_time():

    """
    Gets the current time and returns it.

    We use the most accurate clock available and we return the time in nanoseconds.

    Great for event calculations.

    :return: Time in nano seconds
    :rtype: float
    """

    return time.perf_counter()


def amp_clamp(val):

    """
    Clamps an incoming value to either -1 or 1.

    :param val: Value to clamp
    :type val: float
    :return: Clamped value
    :rtype: float
    """

    if val > 1.0:

        # Too big, clamp it

        return 1.0

    if val < -1.0:

        # Too small, clamp it

        return -1.0

    # No changes necessary

    return val


class BaseModule(object):

    """
    PySynth base module - Class all modules will inherit!

    A 'synth chain' is a collection of modules strung together.
    A 'module' is a component in this chain.
    If a module is 'linked' to another, then it will get it's input from the linked module.

    Here is an example of a synth chain:

    osc -> LP_filt(200) -> asdr(0.2, 0.5, 0.7, 1) -> out

    In this example, an oscillator is attached to a filter,
    which is attached to an asdr envelope, which is then sent to output.

    This class handles modules receiving inputs, traversing the synth,
    starting the synth, and stopping the synth.
    We also keep track of certain attributes, like the frequency of this synth chain,
    as well as the sampling rate of this synth chain.

    Most of these features will be utilized by the sequencer,
    like for changing the frequency of the oscillator(s),
    and for stopping and starting components.

    However, the functionality defined within could be useful to other modules,
    as they may need to access the parameters of modules connected to them.

    If a module inheriting this class defines it's own '__init__()' method,
    then it MUST call the '__init__()' method of the BaseModule it inherits!
    """

    def __init__(self, freq=440.0, samp=44100.0):

        self.input = AudioCollection()  # AudioCollection, allows for multiple inputs into a single node
        self.output = None  # AudioCollection of the node we get connected to
        self.index = 0  # Index of this object
        self._info = ModuleInfo(freq=freq, samp=samp)  # ModuleInfo class for storing info

    def start(self):

        """
        Function called when we are getting prepared for iteration.
        'start' is invoked when '__iter__()' is called.

        The module should assume that if 'start()' is called,
        then the module should be reset to it's initial state.

        The module can put any setup code here they like.
        """

        pass

    def stop(self):

        """
        Function called when we are stopping the chain.
        'stop()' will be invoked by the sequencer when this synth chain this module is apart of it stopped.

        The module can put any stop code here they like.
        """

        pass

    def get_next(self):

        """
        This is the function called when we need an item from the module.
        'get_next()' is invoked upon each call to '__next__'.

        MODULES MUST ALWAYS RETURN FLOATS!

        We only understand floats, and if something else is returned,
        then their is a very high chance that their will be trouble.
        A module must only other types if they understand what is receiving them!

        Most likely, a module's math operations will go here,
        but they don't have too if it makes more sense to put them elsewhere.

        :return: Next value from this item
        :rtype: float
        :raise: NotImplemented: If this class is not overridden
        """

        raise NotImplementedError("This method should be overridden in the child class!")

    def get_input(self):

        """
        Gets a value from the AudioCollection attached to us.
        The user can optionally specify a number of values to retrieve.

        If we receive 'None' from the module connected to us,
        then we will forward it to the module that is ahead of us,
        as 'None' means this synth is stopping, and we should pass it up
        so synths further down the line can know.

        :return: Item from the AudioCollection
        :rtype: float
        """

        # Get an item from the audio collection:

        item = next(self.input)

        if item is None:

            # We are None! Stop this object somehow...

            self.stop()

        return item

    def get_inputs(self, num):

        """
        Gets a number of items from the AudioCollection.

        We return these items as a tuple.

        :param num: Number of items to retrieve
        :type num: int
        :return: Tuple of items from AudioCollection
        """

        # Get a number of items from the collection:

        final = []

        for i in range(num):

            # Get input:

            item = self.get_input()

            if item is None:

                # We are None! Already handled, lets return

                return None

            final.append(i)

        # Convert to tuple and return:

        return tuple(final)

    def bind(self, module):

        """
        Binds an iterable to this class.

        We register the iterable to the AudioCollection,
        and then let it take it from here.

        We also bind their information to us.

        :param module: Iterable to add. This should ideally inherit BaseModule
        :type module: iter
        """

        # Add the iterable to the AudioCollection:

        self.input.add_module(module)

        # Add their info to us:

        self._info = module._info

        # Add ourselves to the output:

        module.output = self

    def unbind(self, module):

        """
        Unbinds an iterable from this class.

        We tell AudioCollection to remove the module.

        :param module: Module to remove
        :type module: iter
        """

        # Remove the module from the AudioCollection:

        self.input.add_module(module)

        # Unregister info:

        module.info = ModuleInfo()

        # Remove ourselves from the output:

        module.output = None

    def traverse_link(self):

        """
        Traverses the links attached to this module.

        We act as a generator, so one could iterate over us in a for loop.
        We utilise recursion to traverse the entire link, and we do it like so:

            - yield ourselves
            - Tell our audio collection to traverse over the items it is connected to
            - yield the items received from the AudioCollection
            - Exit when all links have been traversed

        Because each node has an AudioCollection,
        we will be able to traverse the links until we reach the end.

        This operation can be invoked at any point in the synth,
        and will will traverse back to the start.

        :return: Objects in the link
        :rtype: BaseModule
        """

        # First, yield ourselves:

        yield self

        # Now, continue until we reach a 'StopIteration' exception

        for mod in self.input.traverse_link():

            # yield the module:

            yield mod

    @property
    def info(self):

        """
        Getter for info of this module.

        :return: Info for this module
        :rtype: Moduleinfo
        """

        return self._info

    @info.setter
    def info(self, info):

        """
        Setter for the info of this module.

        We traverse the other links in out chain,
        and set their values to this info instance.

        :param info: ModuleInfo instance to add to module, and links
        :type info: Moduleinfo
        """

        # Add this info to our value:

        self._info = info

        # Add this info to all links:

        for link in self.input._objs:

            # Set the info instance:

            link.info = self._info

    def stop_module(self):

        """
        Meta stop method - Called by other modules when this chain is stopping.

        We do a few things here:

            - Set our 'started' value to False
            - Call our 'stop' method
            - Tell our AudioCollection to stop all input modules

        This is usually called by OutputControl when this chain is stopped,
        but it can also be called by the module itself so it can be removed.
        """

        # Set our started value:

        self.started = False

        # Call our stop method:

        self.stop()

        # Stop all input modules:

        self.input.stop_modules()

    def __iter__(self):

        """
        Prepares this module for operation.

        We do a few things here:

            - Set our index to 0
            - Call our start method
            - Tell our AudioCollection to prepare all input modules
            - Set our 'started' attribute to True

        This allows us to start all sub-modules in the synth chain.
        This utilizes some form of recursion,
        as all modules will call sub-modules to start their own components.

        :return: This module
        :rtype: BaseModule
        """

        # Call the start method:

        self.start()

        # Reset the index value:

        self.index = 0

        # Prepare the sub-modules:

        self.input.start_modules()

        # Set our started value:

        self.info.running = True

        # Return ourselves:

        return self

    def __next__(self):

        """
        Gets the next value in this module and returns it.

        We call 'get_next()' to get this value,
        and then we increase the index of this module.

        :return: Next computed value
        :rtype: float
        """

        val = self.get_next()

        self.index += 1

        return val


class ModuleInfo:

    """
    Common info shared between modules.

    Instead of setting each parameter manually,
    we simply provide a 'ModuleInfo' to each module as it's added to the link.

    This allows us to save time when updating the module info,
    as we only need to change one 'ModuleInfo' instance to change the values of everything.

    Each module creates it's own 'ModuleInfo' instance,
    but it gets overridden when connected to another module.
    """

    def __init__(self, freq=440.0, samp=44100.0):

        self.__slots__ = ['freq', 'samp']  # Slots to to optimise for storage

        #self.freq = AudioValue(freq, 0, samp)  # AudioValue representing the frequency
        self.rate = samp   # Sampling rate of this synth
        self.channels= 1  # Number of channels the synth chain has
        self.running = True  # Value determining if we are running
        self.name = ''  # Meaningful name for this chain

class AudioCollection:

    """
    A collection of audio-generating modules.
    When a value is requested, all the modules are sampled and
    additive synthesis is preformed on them.

    Great for adding the sound of multiple synths together!
    """

    def __init__(self):

        self._objs = []  # Audio objects in our collection

    def add_module(self, node, start=False):

        """
        Adds a PySynth node to the collection.

        We can optionally start the module before adding it.
        Great for if we are adding something on the fly!

        :param node: PySynth node to add
        :type node: BaseModule
        :param start: Value determining if we are starting
        :type start: bool
        """

        if start:

            # Start the module:

            node = iter(node)

        self._objs.append(node)

    def start_modules(self):

        """
        Prepares all modules for iteration.

        We call the '__iter__()' method on each module,
        and let them do the rest.
        """

        # iterate over our modules:

        for mod in self._objs:

            # Prepare the module:

            iter(mod)

    def stop_modules(self):

        """
        Stops all attached modules.
        We call 'stop_module()' and let them do the rest.
        """

        # Iterate over our modules

        for mod in self._objs:

            # Stop the module:

            mod.stop_module()

    def remove_module(self, node):

        """
        Removes a PySynth node from the collection.

        :param node: PySynth node to remove
        """

        self._objs.remove(node)

    def traverse_link(self):

        """
        Iterates over our bound nodes, and yield them.

        We utilise recursion to iterate over the links.
        Once we encounter None, the we are done.

        :return: Modules in the synth
        """

        # Iterate over our modules:

        for synth in self._objs:

            # Get and return the modules:

            for mod in synth.traverse_link():

                # Yield the mod from the module:

                yield mod

        # Now, raise the StopIteration exception to complete:

        raise StopIteration()

    def __iter__(self):

        """
        Prepares the object for iteration.
        :return: This object
        """

        return self

    def __next__(self):

        """
        Gets values from each node and returns it.

        :return: Synthesized values from each node
        :rtype: float
        """

        if not self._objs:

            # Return None

            return None

        final = 0

        for obj in self._objs:

            # Get the next value:

            temp = next(obj)

            if temp is None:

                # We are done, return None

                return None

            # Compute the value

            final = final + temp * 1 / len(self._objs)

        # Done, return the result:

        return final


class AudioMixer(AudioCollection):

    """
    We mix audio from multiple sources.

    Very similar to AudioCollection, 
    excpet that we make a point to check the channel type,
    and mix up/down as necessary.

    We only support stereo audio,
    meaning that we will automatically convert mono to stereo.

    If an input module identifies itself as stereo,
    then we will sample it twice to get the values we need.
    """

    def __next__(self):

        """
        Gets values from each node and returns it.

        We also check if they are multi-channeled,
        and mix them accordingly.

        :return: Tuple contaning values from each channel
        :rtype: tuple
        """

        if not self._objs:

            # Return None

            return None

        final = [0, 0]

        for obj in self._objs:

            # Determine the number of channels:

            if obj.info.channels == 1:

                # One channel, lets sample once and mix it up:

                temp = next(obj)

                if temp is None:

                    # We are done with this node, lets continue:

                    continue

                final[0] = final[0] + temp * 1 / len(self._objs)
                final[1] = final[0] + temp * 1 / len(self._objs)

                continue

            if obj.info.channels == 2:

                # Two channels, lets sample twice and add it:

                temp = next(obj)
                temp2 = next(obj)

                if temp is None or temp2 is None:

                    # We are done with this node, lets continue:

                    continue

                final[0] = final[0] + temp * 1 / len(self._objs)
                final[1] = final[1] + temp2 * 1 / len(self._objs)

                continue

            # Incompatible, continue

            continue

        # Done, return the final result:

        return final
