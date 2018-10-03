#!/bin/python
#ENTech SS
#This document contains misc. data for main script.
import time
import os
import platform
import sys
import subprocess

def startup():
    print("        ______  __  __  ___     _____")
    print("       / ____/ / / / / /   |   / ___/")
    print("      / /     / /_/ / / /| |   \__ \ ")
    print("     / /____ / __  / / ___ |_ ___/ / ")
    print("     \____(_)_/ /_(_)_/  |_(_)____/  ")
    print(" Computerized Home Automation System ver 1.0.0")
    return

def syscheck(servers, serversip, serversph, servstatip, ssh, servstatssh):
    pingstat = None
    print("Checking connectivity to remote servers:")
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
        print("Testing PING for: {}\nI.P Adress: {}\nType of connection: PING".format(actserv, actip))
        pingstat = os.system("ping " + ("-n 1 " if  platform.system().lower()=="windows" else "-c 1 ") + actip)
        if pingstat == 0:
            servstatip.update( {actserv : 'UP' } )
            print("Host {}(I.P: {}) is UP!".format(actserv, actip))
        elif pingstat != None:
            print("Host {}(I.P: {}) is DOWN!\nDiagnossing...".format(actserv, actip))
            time.sleep(2)
            pingdiag(actserv, actip, servstat)
    for i in range(len(servers)):
       # Testing SSH here:
       print("\n#############################################")
       actserv = servers[i]
       actip = serversip[i]
       checkvar = servstatip.get(actserv)
       if checkvar == 'DOWN':
           print("ATTENTION:\n{} is currently DOWN({} failed the PING test) This script will be skipping the SSH test for {}.".format(actserv, actserv, actserv))
           continue
       print("Testing SSH for: {}\nI.P Adress: {}\nType of connection: SSH".format(actserv, actip))
       sshdiag = ssh.stdout.readlines()
       if sshdiag == []:
           ssherror = ssh.stderr.readlines()
           servstatssh.update( {actserv : ssherror } )
           print("\nFailed to conect to {}(I.P: {}) is DOWN!\nDisplaying error here:".format(actserv, actip))
           print(ssherror)
           print("This error will be saved for later diagnosis. Continuing...")
           time.sleep(3)
       else:
            servstatssh.update( {actserv : 'UP' } )
            print("Host {}(I.P: {}) is UP!".format(actserv, actip))
    return    
                                
def pingdiag(actserv, actip, servstat):
    pingstat = None
    print("\nAttempting to try again(This time with more packets!)...\n")
    print("Testing PING for: {}\nI.P Adress: {}\nType of connection: PING".format(actserv, actip))
    pingstat = os.system("ping " + ("-n 4 " if  platform.system().lower()=="windows" else "-c 4 ") + actip)
    if pingstat == 0:
        servstatip.update( {actserv : 'UP' } )
        print("\nHost {}(I.P: {}) Is up!".format(actserv, actip))
        print("Must have been a false alarm or slow connection...\nContinuing!!!!!")
        time.sleep(0.5)
        return
    elif pingstat != None:
        print("\nFailed to connect to {}(I.P: {}) A second time!".format(actserv, actip))
        print("Might be a network error. Trying a genral PING test...\n")
        print("Testing PING for: Google\nDomain: google.com\nType of connection: PING".format(actserv, actip))
        pingstat = os.system("ping " + ("-n 1 " if  platform.system().lower()=="windows" else "-c 4 ") + 'google.com')
        if pingstat == 0:
            servstatip.update( {actserv : 'DOWN' } )
            print("\n#############################################")
            print("\nHost Google(Domain: google.com) is UP!")
            print("This is NOT a network error. Something is wrong with the receiving end(Host: {})".format(actserv))
            print("Check the ehternet cabel and router. Perhapps it got disconnected.")
            print("Also, check the server itself. Maybe it is off, or not reciveing connections.")
            print("Continuing...")
            time.sleep(4)
            return
        elif pingstat != None:
            servstatip.update( {actserv : 'DOWN' } )
            print("\n#############################################")
            print("Host Google(Domain: google.com) is DOWN!")
            print("This means their is proabbly an issue with your wifi.")
            print("Check ALL cables, and check the router.")
            print("Be sure to check the system as well. Perhapps their is something wrong.")
            print("This script will now close, as their is no need to keep checking if the wifi is down")
            empty=input("Press any key to exit...")
            return
            
def mainmenu():
    startup()
    print("\nWelcome to the C.H.A.S Mainframe!\nPlease Select an option:")
    print("1. Display Info\n2. SSH into a server\n3. Open Home Config(NOT YET ACTIVE!)\n4. Exit and open a shell")
    
            
def status(servstatip, servstatssh, servers, serversip, serversph):
    print("Network Satus:")
    for i in range(len(servers)):
        actserv = servers[i]
        actip = serversip[i]
        actph = serversph[i]
        tempstatip = servstatip.get(actserv)
        tempstatssh = servstatssh.get(actserv)
        print("\n+==============================+")
        print("Hostanme: {}".format(actserv))
        print("{}".format(actph))
        print("I.P Address: {}".format(actip))
        print("Server Status: {}".format(tempstatip))
        if tempstatssh != 'UP':
            print("Server SSH Status: DOWN\nDisplaying error:")
            print(tempstatssh)
            print("(Can you make anything of this?")
        else:
            print("Server SSH Status: UP")
        print("\n+==============================+")
    return
    
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    return
