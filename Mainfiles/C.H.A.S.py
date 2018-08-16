#!/bin/python
# ENTech SS
# C.H.A.S Network
# ATTENTION:
# +============================================+
# |This script is for LINUX DEVICES ONLY!!!!   |
# |This script is configured for MY network!   |
# |Using this script will proably not work!    |
# +============================================+
from modules import *
import time
import os
import platform

servers = ['Melanie', 'Lola']
serversip = ['10.0.0.3', '10.0.0.4']
serversph = ['(She\'s One Cool Cat!)', '(She\'s One Smart Girl!)']
servstat = {}
#serverinf = {'serv0':'Melanie', 'serv1':'Lola', 'serv0p':'10.0.0.3', 'serv1p':'10.0.0.4', 'serv0ph':'(She\'s one cool cat!)',
#           'serv1ph':'(She\'s one smart girl!)', 'servn':'11'}

# Displays startup banner
startup()
# Code for checking system
syscheck(servers, serversip, serversph, servstat)
print("Connectivity test complete!")
print("Displaying Network Status Below..\n")
status(servstat, servers, serversip, serversph)
time.sleep(5)
# Code for main menu
clear()
mainmenu()
