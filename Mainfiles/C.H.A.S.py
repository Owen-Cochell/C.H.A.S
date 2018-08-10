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
servers = {'serv0':'Melanie', 'serv1':'Lola', 'serv0p':'10.0.0.3', 'serv1p':'10.0.0.4', 'serv0ph':'(She\'s one cool cat!)',
           'serv1ph':'(She\'s one smart girl!)', 'servn':'11'}
#Displays startup banner
startup()
# Code for checking system
syscheck(servers)
