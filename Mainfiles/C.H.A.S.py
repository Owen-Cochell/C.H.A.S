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
import sys
import subprocess

actserv = None

ssh = subprocess.Popen(["ssh", "%s" % actserv],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

servers = ['Melanie', 'Lola']
serversip = ['10.0.0.3', '10.0.0.4']
serversph = ['(She\'s One Cool Cat!)', '(She\'s One Smart Girl!)']
servstatip = {}
servstatssh = {}
#serverinf = {'serv0':'Melanie', 'serv1':'Lola', 'serv0p':'10.0.0.3', 'serv1p':'10.0.0.4', 'serv0ph':'(She\'s one cool cat!)',
#           'serv1ph':'(She\'s one smart girl!)', 'servn':'11'}

# Displays startup banner
startup()
# Code for checking system
syscheck(servers, serversip, serversph, servstatip, ssh, servstatssh)
print("Connectivity test complete!")
print("Displaying Network Status Below..\n")
status(servstatip, servstatssh, servers, serversip, serversph)
time.sleep(5)
# Code for main menu
clear()
mainmenu()
