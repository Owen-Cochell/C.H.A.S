"""
A simple Prof of Concept extension that showcases CHAS extensions,
while doing something practical at the same time.

We offer tools for enabling and disabling remote outlets,
with given RF codes.
"""

import subprocess

from chaslib.extension import BaseExtension
from chaslib.resptools import keyword_find, key_sta_find


class OutletExtension(BaseExtension):

    """
    Outlet Extension - Allows for the toggling of RF controlled lights using CHAS.

    This is a prof of concept extension, so some advanced features like calibration,
    multiple light toggle, and dependency checking are omitted for simplicity.
    We use 'rfoutlet' to send the codes.

    You can find the source for that here:
    https://github.com/timleland/rfoutlet

    #TODO: Check this:
    Perhaps they will be included at some later date?

    We handle voice data and text data the same, for again, simplicity.

    We utilise the following command structure:

        - 'light enable': Enables the RF outlet
        - 'light disable': Disables the RF outlet

    Our comments in this extension will be very verbose
    (Or at least more verbose than usual),
    so the developer can gain an understanding of the CHAS extension system,
    and how they receive information from CHAS.

    We are automatically loaded into CHAS at run time if we are located in 'extensions/enabled/'.

    Most extensions will follow this format,
    with some more in-depth text parsing to determine the intention of the user.
    """

    def __init__(self):

        # Here, we call __init__() on our superclass, as it has many features and parameters that we need instanciated.
        # The first argument is the extension name, and the second is the extension descritpion.
        # These are very useful for end users, as they will be able to determine what the extension is and what it does.

        super().__init__("RFOutlet", 'Toggles RFOutlets on and off.')

        self.on_code = None  # On code
        self.off_code = None  # Off code

        self.rf_path = '/var/www/rfoutlet/codesend'  # Path to codesend binary

    def match(self, mesg, talk, out):

        """
        Extension match function - This is invoked each time CHAS has process to input.

        Whenever CHAS gets input, be it from voice or text or network,
        it will send the input thorugh each extension to check if any of them handled the information.

        This function is invoked during this process, and it will tell CHAS if the given information is valid and handelable.
        If we are able to do something with the text, then we should do our operation and return 'True'.
        If not, we should return 'False', and CHAS will look elsewhere.

        Here, we check for two statements, 'light on' or 'light off'.
        We will use the internal CHAS text pasring tools to determine if this is what we are looking for.
        'mesg' is the string that contains the input from the user.

        When we want to output something, we use the 'out' class.
        This 'out' class can be a few things:

            - Instance of our CURSES instance for textual output
            - Voice synthesizer for outputting audio information
            - Network logger for sending the output back to clients that requested it

        To us, it does not matter what this output instance is referring to,
        we will output the same content regardless of type. 

        'talk' determines if the user invoked this process via speech.
        Again, we don't care if we are communicating via text or speech,
        we will return the sam ething regardless.

        :param mesg: String contaning input from the user
        :type mesg: str
        :param talk: Boolean determining if we are talking
        :type talk: bool
        :param out: Output object for outputting information
        :return: True for handled content, False for none
        :rtype: bool
        """

        # We use the CHAS text parsers to determine if the string has the content we want.
        # This is not a simple check, this splits the input text up into parts,
        # And determines if the target statement is present.
        # This means inputs like: 'CHAS would you please turn the light on?'
        # Will still resolve to True, so you can talk to CHAS in an intuitive way.
        # key_sta_find() is one of the many CHAS text parsers.
        # The first argument is the string to check, and the second is the statement to find.


        if key_sta_find(mesg, 'light on'):

            # The user wants to turn the outlet on!

            # Now, we must invoke the given binary with the on code using subprocess:

            proc = subprocess.run([self.rf_path, self.on_code])

            # Lets let the user know we have turned on the light:
            # We can also specify a prefix if we are using text output!

            out.add("Turned on the RFLight!", prefix='RFOutlet')

            # Return True to show the request has been handled:

            return True

        if key_sta_find(mesg, 'light off'):

            # The user wants to turn the outlet on!

            # Now, we must invoke the given binary with the off code:

            proc = subprocess.run([self.rf_path, self.on_code])

            # Again, lets let the user know we have turned off the light:

            out.add("Turned off the RFLight!", prefix='RFOutlet')

            # Lets return True to show we have handled it:

            return True

        # There is nothing we can do with the input, lets return False

        return False
