#!/usr/bin/python

import sys
sys.path.append('..')

import pyprofile

profile = pyprofile.pyprofile()

# PIP/MTM IP and port
host = '192.168.207.166'
port = 61315
user = '1'
pwd = 'XXX'
server_type = 'SCA$IBS'

profile.connect(host, port, server_type, user, pwd)
profile.close()