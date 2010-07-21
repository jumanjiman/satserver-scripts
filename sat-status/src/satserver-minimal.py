#!/usr/bin/env python
import xmlrpclib, socket, sys

SATELLITE_URL = "http://%s/rpc/api" % 'YOURSERVERFQDN'
SATELLITE_LOGIN = 'YOURLOGIN'
SATELLITE_PASSWORD = 'YOURPASSWORD'

client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
active_systems = client.system.listActiveSystems(key)
print "Active Systems: %i" % len(active_systems)
for system in active_systems:
	print "\tSystem found was: %s" % system['name']

client.auth.logout(key)

sys.exit(0)
