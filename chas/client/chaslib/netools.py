#!/usr/bin/python

# This file contains methods for handling all things network.

import os
import subprocess
import platform
import time


def netcheck(servers, serversip, serversph, servstatip, servstatssh):

    # Network check code

    # Displaying hosts to test

    print("\nChecking connectivity to remote servers:")
    print("\n+==============================+")
    print("CHECKING THESE SYSTEMS:         ")

    for i in range(len(servers)):
        tempserv = servers[i]
        tempph = serversph[i]

        print(tempserv)
        print(tempph)
        print("+==============================+")

    for i in range(len(servers)):

        # Testing PING here:

        print("\n#############################################")
        actserv = servers[i]
        actip = serversip[i]
        print("Testing PING for: {}\nI.P Address: {}\nType of connection: PING".format(actserv, actip))

        pingstat = os.system(
            "ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + actip)

        if pingstat == 0:

            # If ping is successful,
            # Update server status

            servstatip.update({actserv: 'UP'})
            print("Host {}(I.P: {}) is UP!".format(actserv, actip))

        elif pingstat is None:

            # If ping is not successful,
            # Start ping diagnostics

            print("Host {}(I.P: {}) is DOWN!\nDiagnosing...".format(actserv, actip))
            time.sleep(2)
            pingdiag(actserv, actip, servstatip)

    for i in range(len(servers)):

        # Testing SSH here:

        print("\n#############################################")
        actserv = servers[i]
        actip = servers[i]
        checkvar = servstatip.get(actserv)

        # We use subprocess here to catch the error
        # (Or at least part of it!)

        ssh = subprocess.Popen(["ssh", "%s" % actserv, "hostname"],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        if checkvar == 'DOWN':
            # Server failed the ping test, no need to continue.

            print(
                "ATTENTION:\n{} is currently DOWN({} failed the PING test) This "
                "script will be skipping the SSH test for {}.".format(
                    actserv, actserv, actserv))
            continue

        print("Testing SSH for: {}\nI.P Address: {}\nType of connection: SSH".format(actserv, actip))
        sshdiag = ssh.stdout.readlines()

        if sshdiag is []:

            # Server failed SSH test.
            # Updating status and storing error for later

            ssherror = ssh.stderr.read()
            servstatssh.update({actserv: ssherror})
            print("\nFailed to connect to {}(I.P: {}) is DOWN!\nDisplaying error here:".format(actserv, actip))
            print(ssherror)
            print("This error will be saved for later diagnosis. Continuing...")
            time.sleep(3)

        else:

            # Server passed SSH test!
            # Updating status

            servstatssh.update({actserv: 'UP'})
            print("Host {}(I.P: {}) is UP!".format(actserv, actip))

    return


def netinfo(servstatip, servstatssh, servers, serversip, serversph):

    # Code for displaying Network status

    status(servstatip, servstatssh, servers, serversip, serversph)

    print("\nDo you want to run another network test?")
    inp = input("(Y/N):")

    if inp in ('y', 'Y', 'yes', 'Yes', 'YES'):

        # If the user wants to run another test

        netcheck(servers, serversip, serversph, servstatip, servstatssh)

        empty = input("\nPress enter to continue...")

        return

    return


def status(servstatip, servstatssh, servers, serversip, serversph):

    # Code for displaying network status
    # PING status, SSH status, hostname, ect.

    print("Network Status:")

    for i in range(len(servers)):

        actserv = servers[i]
        actip = serversip[i]
        actph = serversph[i]
        tempstatip = servstatip.get(actserv)
        tempstatssh = servstatssh.get(actserv)

        print("\n+==============================+")
        print("Hostname: {}".format(actserv))
        print("{}".format(actph))
        print("I.P Address: {}".format(actip))
        print("Server Status: {}".format(tempstatip))

        if tempstatssh != 'UP':

            print("Server SSH Status: DOWN\nDisplaying error:")
            print(tempstatssh)
            print("(Can you make anything of this?)")

        else:
            print("Server SSH Status: UP")

        print("+==============================+")
    return


def pingdiag(actserv, actip, servstatip):
    # Ping diagnostics

    print("\nAttempting to try again(This time with more packets!)...\n")
    print("Testing PING for: {}\nI.P Address: {}\nType of connection: PING".format(actserv, actip))

    pingstat = os.system("ping " + ("-n 4 " if platform.system().lower() == "windows" else "-c 4 ") + actip)

    if pingstat == 0:

        # If increased packet test was successful

        servstatip.update({actserv: 'UP'})
        print("\nHost {}(I.P: {}) Is up!".format(actserv, actip))
        print("Must have been a false alarm or slow connection...\nContinuing!!!!!")
        time.sleep(0.5)
        return

    elif pingstat != 0:

        # If increased packet test failed

        print("\nFailed to connect to {}(I.P: {}) A second time!".format(actserv, actip))
        print("Might be a network error. Trying a general PING test...\n")
        print("Testing PING for: Google\nDomain: google.com\nType of connection: PING".format(actserv, actip))
        pingstat = os.system("ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 4 ") + 'google.com')

        if pingstat == 0:

            # Code for is wifi is up

            servstatip.update({actserv: 'DOWN'})
            print("\n#############################################")
            print("\nHost Google(Domain: google.com) is UP!")
            print("This is NOT a network error. Something is wrong with the receiving end(Host: {})".format(actserv))
            print("Check the ethernet cable and router. Perhaps it got disconnected.")
            print("Also, check the server itself. Maybe it is off, or not receiving connections.")
            print("Continuing...")
            time.sleep(4)
            return

        elif pingstat != 0:

            # Code for if wifi is down

            servstatip.update({actserv: 'DOWN'})
            print("\n#############################################")
            print("Host Google(Domain: google.com) is DOWN!")
            print("This means their is probably an issue with your wifi.")
            print("Check ALL cables, and check the router.")
            print("Be sure to check the system as well. Perhaps their is something wrong.")
            print("This script will now close, as their is no need to keep checking if the wifi is down")
            empty = input("Press any key to exit...")
            return


def dev_trigger(tog, loc, id, serversip):

    cmd = ('python3 outlet.py {} {} {}'.format(tog, loc, id))

    ssh_cmd(serversip[2], 'pi', cmd)

    return


def ssh_cmd(ip, usr, com):

    ssh = subprocess.Popen(
        ['ssh', '{}@{}'.format(usr, ip), com],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=-1)

    output, error = ssh.communicate()

    if ssh.returncode != 0:

        print("\n+==========================================+")
        print("\nAttention:\nA SSH Error occurred!")
        print("Displaying error/output below:")
        print("\n--== Output: ==--\n{}".format(output))
        print("\n--== Error: ==--\n{}".format(error))
        print("Return code: {}".format(ssh.returncode))
        print("\n(Can you make anything of this?)")
        empty = input("Press enter to continue...")
        return

    print("SSH command completed successfully!")
    return
