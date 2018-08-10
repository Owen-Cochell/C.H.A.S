#!/bin/python
#ENTech SS
#This document contains misc. data for main script.
import time
import os
import platform

class serverinfo:

    def __init__(self, ip, hostname, typec):
        self.ip = ip
        self.hostname = hostname
        self.typec = typec
        return

def startup():
    print("        ______  __  __  ___     _____")
    print("       / ____/ / / / / /   |   / ___/")
    print("      / /     / /_/ / / /| |   \__ \ ")
    print("     / /____ / __  / / ___ |_ ___/ / ")
    print("     \____(_)_/ /_(_)_/  |_(_)____/  ")
    print(" Computerized Home Automation System ver 1.0.0")
    return

def syscheck(servers):
    through=0
    servn = servers.get('servn')
    pingstat = None
    print("Checking connectivity to remote servers:")
    print("\n+==============================+")
    print("CHECKING THESE SYSTEMS:         ")
    print("{serv0}                         ".format(**servers))
    print("{serv0ph}                        ".format(**servers))
    print("{serv1}                         ".format(**servers))
    print("{serv1ph}                        ".format(**servers))
    print("+==============================+")
    for x in str(servn):
        print("\n#############################################")
        actserv = servers.get('serv0'.format(x))
        actip = servers.get('serv0p'.format(x))
        if through==1:
            actserv = servers.get('serv1'.format(x))
            actip = servers.get('serv1p'.format(x))
        print("Testing PING for: {}\nI.P Adress: {}\nType of connection: PING".format(actserv, actip))
        pingstat = os.system("ping " + ("-n 1 " if  platform.system().lower()=="windows" else "-c 1 ") + actip)
        if pingstat == 0:
            print("Host {}(I.P: {}) is UP!".format(actserv, actip))
        elif pingstat != None:
            print("Host {}(I.P: {}) is DOWN!\nDiagnossing...".format(actserv, actip))
            time.sleep(2)
            pingdiag(actserv, actip)
        through=1
    return    
                                
def pingdiag(actserv, actip):
    pingstat = None
    print("\nAttempting to try again(This time with more packets!)...")
    print("Testing PING for: {}\nI.P Adress: {}\nType of connection: PING".format(actserv, actip))
    pingstat = os.system("ping " + ("-n 4 " if  platform.system().lower()=="windows" else "-c 4 ") + actip)
    if pingstat == 0:
        print("Host {}(I.P: {}) Is up!".format(actserv, actip))
        print("Must have been a false alarm...\nContinueing!!!!!")
        return
    elif pingstat != None:
        print("Failed to connect to {}(I.P: {}) A second time!".format(actserv, actip))
        print("Might be a network error. Trying a genral PING test...")
        print("Testing PING for: Google\nDomain: google.com\nType of connection: PING".format(actserv, actip))
        pingstat = os.system("ping " + ("-n 1 " if  platform.system().lower()=="windows" else "-c 4 ") + 'google.com')
        if pingstat == 0:
            print("Host Google(Domain: google.com) is UP!")
            print("This is NOT a network error. Something is wrong with the receiving end(Host: {})".format(actserv))
            print("Check the ehternet cabel and router. Perhapps it got disconnected.")
            print("Also, check the server itself. Maybe it is off.")
            print("Continueing...")
            time.sleep(4)
            return
        elif pingstat != None:
            print("Host Google(Domain: google.com) is DOWN!")
            print("This means their is proabbly an issue with your wifi.")
            print("Check ALL cables, and check the router.")
            print("Be sure to check the system as well. Perhapps their is something wrong.")
            print("Continuing...")
            time.sleep(4)
            return
            
            
