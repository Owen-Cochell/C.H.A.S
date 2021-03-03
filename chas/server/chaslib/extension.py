# This file contains a C.H.A.S extension mold

from chaslib.device import Devices
from chaslib.sound.base import OutputHandler
from chaslib.resptools import keyword_find, key_sta_find, string_clean
from chaslib.misctools import get_logger

import os
import pkgutil
import inspect


class BaseExtension(object):

    """
    Extension base class.
    All CHAS extensions must inherent this class to be loaded
    """

    def __init__(self, name, description, priority=3):

        self.name = name  # Name of the extension
        self.description = description  # Extension Description
        self.priority = priority  # Priority value of the extension, determines order
        self.enabled = False  # Value determining if extension is enabled
        self.uuid = ''  # UUID of the extension
        self.help = []  # Dictionary storing help information

    def _bind_chas(self, chas):

        """
        Binds CHAS masterclass to the extension

        :param chas: Instance of CHAS Masterclass
        """

        self.chas = chas

    def match(self, mesg, talk, win):

        """
        Default match method for extensions
        Should be overridden in the child class.

        :param mesg: Message to be processed
        :param talk: Boolean determining if we are talking
        :param win: CHAS window object
        :return:
        """

        return False

    def enable(self):

        """
        Parent function called when the extension is enabled
        Defined here in case user does not provide start method
        """

        pass

    def disable(self):

        """
        Parent function called when extension is disabled
        Defined here in case user does not provide start method
        """

        pass

    def load(self):

        """
        Parent function called when the extension is first loaded,
        regardless of weather it's being enabled or disabled.
        """

        pass

    def unload(self):

        """
        Method called when the extension is removed from our cache.
        This is the final method that will be called before the extension is removed via garbage collection.

        The function should finish up everything that the extension is doing.
        'stop()' will always be called before this function is called.
        """

        pass

    def add_help(self, name, desc, usage=''):

        """
        Adds an entry to the help menu of the extension.
        Ideally, this should display relevant keywords or commands that
        your plugin looks for, and should display some usage information.

        :param name: Name of the command to register
        :param desc: Description of the command to register
        :param usage: Usage of the command to register
        """

        pass


class Extensions:

    """
    Class that maintains and handles extensions
    """

    def __init__(self, chas):

        self.chas = chas  # CHAS Masterclass instance
        self._enabled_directory = [os.path.join(self.chas.settings.extension_dir, 'enabled')]
        self._disabled_directory = [os.path.join(self.chas.settings.extension_dir, 'disabled')]
        self._enabled_extensions = []  # List of enabled extensions
        self._disabled_extensions = []  # List of disabled extensions
        self._core = CoreTools()  # Builtin CHAS functions
        self._name = 'BaseExtension'  # Name of extension parent class
        self.log = get_logger("CHAS:EXTEN")

        self._core.chas = self.chas  # Binding the CHAS masterclass to the Core Tools extension

    def get_extensions(self):

        """
        Generates a dictionary of extension instances sorted by enabled status
        :return:
        """

        return {'enabled': self._enabled_extensions, 'disabled': self._disabled_extensions}

    def disable_extension(self, name, stop=True):

        """
        Disables a CHAS extension using th given name.

        We return True if successful, False if not.

        :param name: Name of extension to disable
        :arg stop: Call 'stop' method before disabling it
        """

        self.log.info("Disabling extension: [{}]...".format(name))

        # Searching for extension:

        ext = self.find(name)

        if not ext:

            # Could not find extension, lets exit:

            self.log.warning("Could not disable extension [{}]!".format(name))

            return False

        if ext in self._enabled_extensions:

            self._enabled_extensions.remove(ext)

        if stop:

            # Stopping extension:

            try:

                # Attempting to disable the extension:

                ext.disable()

            except Exception as e:

                # Lets log and continue:

                self.log.warning("Exception occurred when disabling extension: [{}]!".format(name), exc_info=e)
                self.log.warning("We will skip 'disable()' and force remove [{}]".format(name))

        # Disabling extension:

        ext.enabled = False

        # Adding extension to disabled extension list

        self._disabled_extensions.append(ext)

        self.log.info("Successfully disabled extension [{}]!".format(name))

        return True

    def enable_extension(self, name):

        """
        Enables extension by name.

        We call 'enable()' on the extension,
        so it can run any setup code that it needs.
        If this call fails, then we will refuse to load the extension.

        :param name: Name of the extension
        :return: True for success, False for failure
        :rtype: bool
        """

        self.log.info("Enabling extension [{}]...".format(name))

        # Searching for extension:

        ext = self.find(name)

        if not ext:

            # We failed to find the extension! log and return

            self.log.warning("Unable to enable extension [{}] - Name not found!".format(name))

            return False

        # Removing extension from disabled

        if ext in self._disabled_extensions:

            self._disabled_extensions.remove(ext)

        # Starting extension:

        ext.enabled = True

        try:

            ext.enable()

        except Exception as e:

            # Error occurred, logging and handling
            # Skipping over extension start and returning failure

            self.log.warning("Exception occurred when enabling [{}]!".format(name), exc_info=e)
            self.log.warning("NOT enabling extension [{}]!".format(name))

            ext.enabled = False

            self._disabled_extensions.append(ext)

            return False

        # Enabling extension

        # Adding extension to enabled list

        if ext not in self._enabled_extensions:

            self._enabled_extensions.append(ext)

        self.log.info("Successfully enabled extension [{}]!".format(name))

        return True

    def parse_extensions(self):

        """
        Method for parsing and loading extensions
        """

        self.log.info("Parsing and rebuilding extension cache...")

        # Clearing loaded extensions(if any)

        self.stop()

        self._enabled_extensions.clear()
        self._disabled_extensions.clear()

        # Loading enabled extensions

        val = self._parse_directory(self._enabled_directory, self._enabled_extensions)

        if not val:

            # Something went wrong, probably logged already

            self.log.warn("Unable to parse extentions!")

            return False

        self.log.info("Found [{}] extensions to enable".format(len(self._enabled_extensions)))

        # Enabling extensions that are enabled

        for ext in self._enabled_extensions:

            # Enabling extension:

            self.enable_extension(ext.name)

        self.log.info("Enabled [{}] extensions".format(len(self._enabled_extensions)))

        # Loading disabled extensions

        val = self._parse_directory(self._disabled_directory, self._disabled_extensions)

        self.log.info("Found [{}] disabled extensions".format(len(self._disabled_extensions)))

        # Sorting extension lists

        self._enabled_extensions.sort(key=self._get_priority)
        self._disabled_extensions.sort(key=self._get_priority)

        return True

    def handel(self, sent, talk, win):

        """
        Query Extensions for handling of user given text.

        :param sent: Sentence typed/spoken by user
        :param win: CHAS chat window object to write to
        :param talk: Boolean determining if user is talking
        """

        # Checking CORE features first

        val = self._core.handel(sent, talk, win)

        if val:

            # CORE handled output

            return True

        # Checking other extensions

        for ext in self._enabled_extensions:

            val = ext.match(sent, talk, win)

            if val:

                return True

        return False

    def stop(self):

        """
        Disabled all extensions,
        Calls the stop() method on each extension,
        and the unloads them.
        """

        for ext in self._enabled_extensions:

            # Disabling extension

            self.disable_extension(ext.name)

    def find(self, name, disabled=False):

        """
        Finds and returns an extension by name.

        If the extension is not found,
        then we we return False.

        By default, we search only enabled extensions.
        If 'disabled' is True, then we search in the disabled category.

        :param name: Name of the extension to search for
        :type name: str
        :param disabled: Determines if we should search disabled extensions
        :type disabled: bool
        :return: Instance of the extension
        :rtype: BaseExtension
        """

        self.log.debug("Searching for extension with name: [{}]".format(name))

        # Determine which list to search:

        if disabled:

            # Search through disabled extensions:

            collec = self._disabled_extensions

        else:

            # Search through enabled extensions

            collec = self._enabled_extensions

        # Search through our collection:

        for ext in collec:

            # Check if the name is valid:

            if ext.name == name:

                # Found our extension!

                self.log.debug("Found extension [{}]!".format(name))

                return ext

        self.log.debug("Unable to find extension [{}]!".format(name))

    def _parse_directory(self, direct, final):

        """
        Parses extensions from specified location
        :param direct: Path to directory location
        :param final: List object to add extensions to
        :return:
        """

        # Iterating over every file in specified directory

        try:

            for finder, name, _ in pkgutil.iter_modules(path=direct):

                # Loading module for inspection

                mod = finder.find_module(name).load_module(name)

                for member in dir(mod):

                    # Iterating over builtin attributes

                    obj = getattr(mod, member)

                    # Checking if extension is class

                    if inspect.isclass(obj):

                        # Iterating over each parent

                        for parent in obj.__bases__:

                            # Checking class parent

                            if self._name is parent.__name__:

                                # Found a CHAS extension

                                obj._bind_chas(obj, self.chas)

                                plug = obj()

                                plug.load()

                                final.append(plug)

        except Exception as e:

            # Something went wrong

            self.log.error("Error occured while trversing: {}".format(e))

        return True

    def _get_priority(self, ext):

        """
        Gets extension priority
        To be used by the sorting method in 'parse_extensions()'.

        :param ext: BaseExtension instance
        :return: Extension priority
        :rtype: int
        """

        return ext.priority


class CoreTools(BaseExtension):

    """
    CHAS builtins
    Handles events such as changing extensions, personalities, ect.
    These are builtin commands that can't be removed, as they are necessary for CHAS to function.
    """

    def __init__(self):

        super(CoreTools, self).__init__('CoreTools', 'CHAS Core Tools', priority=-1)
        self.out = 'CORE:TOOLS'
        self.sep = "+==================================================+"  # Seperator for text

    def handel(self, mesg, talk, win):

        """
        Handels input from user.

        :param mesg: Input from us er
        :param talk: Boolean determining if we are talking
        :param win: Output object
        :return:
        """

        if keyword_find(mesg, ['extension', 'plugin']):

            # Dealing with plugins here:

            if keyword_find(mesg, ['reload', 'refresh']):

                # Reload the extensions reconfigure them

                win.add("[Reloading and reconfiguring extensions]", prefix=self.out)
                win.add("[Please wait...]", prefix=self.out)

                val = self.chas.extensions.parse_extensions()

                if val:

                    # Procedure was a success

                    win.add("[Task Completed Successfully]", prefix=self.out)

                    return True

                win.add("[Task Failed]", prefix=self.out)
                win.add("[Check usage logs for more information]", prefix=self.out)

                return True

            if keyword_find(mesg, ['list', 'show']):

                # User wants to see all extensions

                # Getting dictionary from extension manager

                dic = self.chas.extensions.get_extensions()

                if talk:

                    # User is expecting audio output:

                    win.add("Listing Enabled Extensions:")

                    for ext in dic['enabled']:

                        # Separating info for pausing

                        win.add(ext.name)
                        win.add(ext.description)

                    win.add("Listing Disabled Extensions:")

                    for ext in dic['disabled']:

                        # Separating info for for pausing

                        win.add(ext.name)
                        win.add(ext.description)

                    win.add("End listing extensions.")

                    return True

                else:

                    # User wants text-based output

                    win.add("+==================================================+", prefix=self.out)

                    win.add("[Enabled Extensions:]", prefix=self.out)

                    for ext in dic['enabled']:

                        win.add(" - {}: {}".format(ext.name, ext.description), prefix=self.out)

                    win.add("[Disabled Extensions:]", prefix=self.out)

                    for ext in dic['disabled']:

                        win.add(" - {}: {}".format(ext.name, ext.description))

                    win.add("+==================================================+", prefix=self.out)

                    return True

            if keyword_find(mesg, 'disable'):

                # User wants to disable an extension

                # Getting name from string

                index = mesg.index(" disable ") + 9

                val = mesg[index:]

                win.add("[Disabling Extension: {}]".format(val), prefix=self.out)

                # Disabling name

                ret = self.chas.extensions.disable_extension(val)

                if ret:

                    win.add("[Successfully Disabled Extension: {}]".format(val), prefix=self.out)

                    return True

                win.add("[Failed to disable extension: {}]".format(val), prefix=self.out)
                win.add("[Check usage logs more more details]", prefix=self.out)
                win.add("[The extension was unloaded, and will not be used again for the remainder of this runtime]")

                return True

            if keyword_find(mesg, 'enable'):

                # User wants to enable an extension

                # Getting name from string

                index = mesg.index(" enable ") + 8

                val = mesg[index:]

                win.add("[Enabling Extension: {}]".format(val), prefix=self.out)

                # Enabling name

                ret = self.chas.extensions.enable_extension(val)

                if ret:

                    win.add("[Successfully Enabled Extension: {}]".format(val), prefix=self.out)

                    return True

                win.add("[Failed to enable extension: {}]".format(val), prefix=self.out)
                win.add("[Check usage logs more more details]", prefix=self.out)

                return True

        if keyword_find(mesg, ['personality', 'intelligence']):

            # Dealing with personalities

            if keyword_find(mesg, 'reload'):

                # User wants to reload personalities

                win.add("[Reloading and reconfiguring personalities]", prefix=self.out)
                win.add("[Please wait...]", prefix=self.out)

                val = self.chas.person.parse_personalities()

                if val:

                    # Successfully parsed personalities

                    win.add("[Task Completed Successfully]", prefix=self.out)

                    return True

                # Did not complete task

                win.add("[Task Failed]", prefix=self.out)
                win.add("[Check usage logs for more information]", prefix=self.out)

                return True

            if keyword_find(mesg, 'list'):

                # User wants to see all personalities

                # Getting personalities from personality manager

                dic = self.chas.person.get_personalities()

                if talk:

                    # User is expecting audio output:

                    win.add("Listing Available Personalities:")

                    for per in dic:

                        # Separating info for pausing

                        win.add(per.name)
                        win.add(per.description)

                    win.add("End listing personalities.")

                    return True

                else:

                    # User wants text-based output

                    win.add("+==================================================+", prefix=self.out)

                    win.add("[Available Personalities:]", prefix=self.out)

                    for per in dic:

                        win.add(" - {}: {} {}".format(per.name, per.description,
                                                      ("< Selected" if per.selected else '')), prefix=self.out)

                    win.add("+==================================================+", prefix=self.out)

                    return True

            if keyword_find(mesg, 'select'):

                # User wants to select a personality

                # Getting index

                index = mesg.index(' select ') + 8

                val = mesg[index:]

                win.add("[Selecting personality: {}]".format(val), prefix=self.out)
                win.add("[Please wait, this could take some time depending on the personality...]", prefix=self.out)

                ret = self.chas.person.select(val)

                if ret:

                    win.add("[Successfully selected personality: {}]".format(val), prefix=self.out)

                    return True

                win.add("[Failed to select personality: {}]".format(val), prefix=self.out)
                win.add("[See usage logs for more details]", prefix=self.out)

                return True

        if keyword_find(mesg, ['net']):

            # Dealing with networking

            if keyword_find(mesg, 'status'):

                # Get stats from networking component:

                host = self.chas.net.host
                port = self.chas.net.port

                if self.chas.server:

                    if talk:

                        # Lets say out loud

                        win.add("Stats for socket server")
                        win.add("Listening on host {} on port {}".format(host, port))
                        win.add("{} clients connected".format(len(self.chas.devices)))

                        return

                    # Lets print to the terminal:

                    win.add(self.sep, prefix=self.out)
                    win.add("[Socket Server Stats:]", prefix=self.out)
                    win.add(" - Hostname: {}".format(host), prefix=self.out)
                    win.add(" - Port: {}".format(port), prefix=self.out)
                    win.add(" - Clients Connected: {}".format(len(self.chas.devices)), prefix=self.out)
                    win.add(self.sep, prefix=self.out)

                    return

                # Working with a client:

                if talk:

                    # Lets say out loud

                    win.add("Stats for socket client")
                    
                    if self.chas.server is None:

                        # We are not connected:

                        win.add("Socket client is not connected")

                    else:

                        win.add("Socket client is connected")
                    
                    win.add("Server address is {}".format(self.chas.net.hostname))
                    win.add("Server port is {}".format(self.chas.net.port))

                    return

                # Lets print out to terminal:

                win.add(self.sep, prefix=self.out)
                win.add("[Socket Client Stats:]", prefix=self.out)
                win.add("[Connected: {}]".format(self.chas.server is not None), prefix=self.out)
                win.add(" - Address: {}".format(host), prefix=self.out)
                win.add(" - Port: {}".format(port), prefix=self.out)
                win.add(self.sep, prefix=self.out)

                return

        if keyword_find(mesg, ['audio']):

            # Dealing with audio commands

            if keyword_find(mesg, ['list']):

                # User wants a list of all audio nodes:

                nodes = self.chas.sound._input._objs

                if talk:

                    # We are talking, lets give a concice list:

                    win.add("Connected audio nodes")

                    for node in nodes:

                        win.add("{} with name {}".format(type(node), node.name))

                    return

                # Lets provide a textual representation of the audio:

                win.add(self.sep, prefix=self.out)
                win.add("[Connected audio nodes:]", prefix=self.out)
                
                if not nodes:

                    # No nodes loaded! Lets print that

                    win.add("No audio nodes loaded!", prefix=self.out)

                for node in nodes:

                    win.add(" - [{}]: {}".format(type(node), node.name), prefix=self.out)

                win.add(self.sep, prefix=self.out)

                return

        if 'help ' == string_clean(mesg):

            # User wants help

            pass

        return False
