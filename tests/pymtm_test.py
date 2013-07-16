#!/usr/bin/python

'''
simple test using a custom server running in PIP as simple as:

ZFPSV(IM)
        I $E(IM,1,5)="echo " quit $E(IM,6,99999)
        Q ""
'''

import sys
sys.path.append('..')

import pymtm

mtm = pymtm.pymtm()

# PIP/MTM IP and port
host = '192.168.207.166'
port = 61314
msg = "echo 123"

mtm.connect(host, port)
assert mtm.exchange_message(msg) == "123"
mtm.close()