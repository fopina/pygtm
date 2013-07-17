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

# backup current ICITY
rows,col_types = profile.executeSQL('SELECT ICITY FROM CUVAR')
assert col_types[0] == 'T'
old_city = rows[0]

# update ICITY to 'TEST'
profile.executeSQL('UPDATE CUVAR SET ICITY = ?','TEST')

# verify it was updated
rows,col_types = profile.executeSQL('SELECT ICITY FROM CUVAR')
assert col_types[0] == 'T'
assert rows[0] == 'TEST'

# set it back to old value
profile.executeSQL('UPDATE CUVAR SET ICITY = ?',old_city)
rows,col_types = profile.executeSQL('SELECT ICITY FROM CUVAR')
assert col_types[0] == 'T'
assert rows[0] == old_city

profile.close()