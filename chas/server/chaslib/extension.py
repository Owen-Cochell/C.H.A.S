# This file contains a C.H.A.S extension mold

import os
import pkgutil
import inspect
from chaslib.resptools import keyword_find, key_sta_find, string_clean


class Extension(object):

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
        :return:
        """

        self.chas = chas

    def match(self, mesg, talk, win):

        """
        Default match method for extensions
        Should be overidden in the child class
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
        :return:
        """

        pass

    def disable(self):

        """
        Parent function called when extension is disabled
        Defined here in case user does not provide start method
        :return:
        """

        pass

    def load(self):

        """
        Parent function called when the extension is first loaded,
        regardless of weather it's being enabled or disabled.
        :return:
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
        :return:
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
        self._name = 'Extension'  # Name of extension parent class

        self._core.chas = self.chas  # Binding the CHAS masterclass to the Core Tools extension

    def get_extensions(self):

        """
        Generates a dictionary of extension instances sorted by enabled status
        :return:
        """

        return {'enabled': self._enabled_extensions, 'disabled': self._disabled_extensions}

    def disable_extension(self, name, stop=True):

        """
        Disables CHAS extension
        :param name: Name of extension to disable
        :arg stop: Call 'stop' method before disabling it
        :return:
        """

        # Searching for extension:

        for ext in self._enabled_extensions:

            # Checking name:

            if ext.name == name:

                # Found our extension

                # Removing extension from the enabled list

                self._enabled_extensions.remove(ext)

                if stop:

                    # Stopping extension:

                    try:

                        ext.disable()

                    except:

                        continue

                # Disabling extension:

                ext.enabled = False

                # Adding extension to disabled extension list

                self._disabled_extensions.append(ext)

                return True

        return False

    def stop(self):

        """
        Disabled all extensions,
        Calls the stop() method
        :return:
        """

        for ext in self._enabled_extensions:

            # Disabling extension

            self.disable_extension(ext.name)

    def enable_extension(self, name):

        """
        Enables extension by name
        :param name: Name of the extension
        :return:
        """

        # Searching for extension:

        for ext in self._disabled_extensions:

            # Checking extension name

            if ext.name == name:

                # Found our extension

                # Removing extension from disabled

                self._disabled_extensions.remove(ext)

                # Starting extension:

                ext.enabled = True

                try:

                    ext.enable()

                except:

                    # Error occurred, logging and handling
                    # Skipping over extension start and returning failure

                    ext.enabled = False

                    self._disabled_extensions.append(ext)

                    return False

                # Enabling extension

                # Adding extension to enabled list

                self._enabled_extensions.append(ext)

                return True

        return False

    def parse_extensions(self):

        """
        Method for parsing and loading extensions
        :return:
        """

        # Clearing loaded extensions(if any)

        self.stop()

        self._enabled_extensions.clear()
        self._disabled_extensions.clear()

        # Loading enabled extensions

        val = self._parse_directory(self._enabled_directory, self._enabled_extensions)

        if not val:

            # Something went wrong, probably logged already

            return False

        # Enabling extensions that are enabled

        for ext in self._enabled_extensions:

            # Enabling extension

            ext.enabled = True

            # Starting extension

            try:

                ext.enable()

            except:

                # Error occurred, logging and handling
                # Skipping starting extension

                ext.disable()
                self._enabled_extensions.remove(ext)
                self._disabled_extensions.append(ext)

                continue

        # Loading disabled extensions

        val = self._parse_directory(self._disabled_directory, self._disabled_extensions)

        # Sorting extension lists

        self._enabled_extensions.sort(key=self._get_priority)
        self._disabled_extensions.sort(key=self._get_priority)

        return True

    def handel(self, sent, talk, win):

        """
        Query Extensions for handling of user given text
        :param sent: Sentence typed/spoken by user
        :param win: CHAS chat window object to write to
        :param talk: Boolean determining if user is talking
        :return:
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

    def _parse_directory(self, direct, final):

        """
        Parses extensions from specified location
        :param direct: Path to directory location
        :param final: List object to add extensions to
        :return:
        """

        # Iterating over every file in specified directory

        print("Path: {}".format(direct))

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

                                print(obj)

                                obj._bind_chas(obj, self.chas)

                                plug = obj()

                                plug.load()

                                final.append(plug)

        except Exception as e:

            # Something went wrong

            print("Their was an error while parsing extensions: {}".format(e))

            return False

        return True

    def _get_priority(self, ext):

        """
        Gets extension priority
        To be used by the sorting method in 'parse_extensions()'
        :param ext: Extension instance
        :return:
        """

        return ext.priority


class CoreTools(Extension):

    """
    CHAS builtins
    Handles events such as changing extensions, personalities, ect.
    These are builtin commands that can't be removed, as they are necessary for CHAS to function.
    """

    def __init__(self):

        super(CoreTools, self).__init__('CoreTools', 'CHAS Core Tools', priority=-1)
        self.out = 'CORE:TOOLS'

    def handel(self, mesg, talk, win):

        """
        Handels input from user
        :param mesg: Input from us er
        :param talk: Boolean determining if we are talking
        :param win: Output object
        :return:
        """

        if keyword_find(mesg, ['extension', 'plugin']):

            # Dealing with plugins here:

            if keyword_find(mesg, ['reload', 'refresh']):

                # Reload the extensions reconfigure them

                win.add("[Reloading and reconfiguring extensions]", output=self.out)
                win.add("[Please wait...]", output=self.out)

                val = self.chas.extensions.parse_extensions()

                if val:

                    # Procedure was a success

                    win.add("[Task Completed Successfully]", output=self.out)

                    return True

                win.add("[Task Failed]", output=self.out)
                win.add("[Check usage logs for more information]", output=self.out)

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

                    win.add("+==================================================+", output=self.out)

                    win.add("[Enabled Extensions:]", output=self.out)

                    for ext in dic['enabled']:

                        win.add(" - {}: {}".format(ext.name, ext.description), output=self.out)

                    win.add("[Disabled Extensions:]", output=self.out)

                    for ext in dic['disabled']:

                        win.add(" - {}: {}".format(ext.name, ext.description))

                    win.add("+==================================================+", output=self.out)

                    return True

            if keyword_find(mesg, 'disable'):

                # User wants to disable an extension

                # Getting name from string

                index = mesg.index(" disable ") + 9

                val = mesg[index:]

                win.add("[Disabling Extension: {}]".format(val), output=self.out)

                # Disabling name

                ret = self.chas.extensions.disable_extension(val)

                if ret:

                    win.add("[Successfully Disabled Extension: {}]".format(val), output=self.out)

                    return True

                win.add("[Failed to disable extension: {}]".format(val), output=self.out)
                win.add("[Check usage logs more more details]", output=self.out)
                win.add("[The extension was unloaded, and will not be used again for the remainder of this runtime]")

                return True

            if keyword_find(mesg, 'enable'):

                # User wants to enable an extension

                # Getting name from string

                index = mesg.index(" enable ") + 8

                val = mesg[index:]

                win.add("[Enabling Extension: {}]".format(val), output=self.out)

                # Enabling name

                ret = self.chas.extensions.enable_extension(val)

                if ret:

                    win.add("[Successfully Enabled Extension: {}]".format(val), output=self.out)

                    return True

                win.add("[Failed to enable extension: {}]".format(val), output=self.out)
                win.add("[Check usage logs more more details]", output=self.out)

                return True

        if keyword_find(mesg, ['personality', 'intelligence']):

            # Dealing with personalities

            if keyword_find(mesg, 'reload'):

                # User wants to reload personalities

                win.add("[Reloading and reconfiguring personalities]", output=self.out)
                win.add("[Please wait...]", output=self.out)

                val = self.chas.person.parse_personalities()

                if val:

                    # Successfully parsed personalities

                    win.add("[Task Completed Successfully]", output=self.out)

                    return True

                # Did not complete task

                win.add("[Task Failed]", output=self.out)
                win.add("[Check usage logs for more information]", output=self.out)

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

                    win.add("+==================================================+", output=self.out)

                    win.add("[Available Personalities:]", output=self.out)

                    for per in dic:

                        win.add(" - {}: {} {}".format(per.name, per.description,
                                                      ("< Selected" if per.selected else '')), output=self.out)

                    win.add("+==================================================+", output=self.out)

                    return True

            if keyword_find(mesg, 'select'):

                # User wants to select a personality

                # Getting index

                index = mesg.index(' select ') + 8

                val = mesg[index:]

                win.add("[Selecting personality: {}]".format(val), output=self.out)
                win.add("[Please wait, this could take some time depending on the personality...]", output=self.out)

                ret = self.chas.person.select(val)

                if ret:

                    win.add("[Successfully selected personality: {}]".format(val), output=self.out)

                    return True

                win.add("[Failed to select personality: {}]".format(val), output=self.out)
                win.add("[See usage logs for more details]", output=self.out)

                return True

        if 'help ' == string_clean(mesg):

            # User wants help

            pass

        return False
