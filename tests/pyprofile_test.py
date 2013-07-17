#!/usr/bin/python

import sys
sys.path.append('..')

import pyprofile

# PIP/MTM IP and port configuration
###################################
host = '192.168.207.166'
port = 61315
user = '1'
pwd = 'XXX'
server_type = 'SCA$IBS'
###################################

def test_sql():
	profile = pyprofile.pyprofile()
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

def test_mrpc():
	profile = pyprofile.pyprofile()
	profile.connect(host, port, server_type, user, pwd)

	# test MRPCs (only 121 and 155 available in core PIP)
	# using 155 for assertion, returns an SQL query response formatted in HTML
	assert profile.executeMRPC('155','SELECT TJD FROM CUVAR').find('<th title="CUVAR.TJD date">System<br>Processing<br>Date</th>') > -1

	profile.close()

def main():
	test_sql()
	test_mrpc()

if __name__ == '__main__':
	main()