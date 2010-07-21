#!/usr/bin/env python

"""
Authored by Brent Holden
Copyright 2008, Red Hat, Inc

Licensed under the GPLv2

"""

import xmlrpclib
import socket
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--login", dest="login", help="Login user for satellite", metavar="LOGIN")
parser.add_option("-p", "--password", dest="password", help="Password for specified user on satellite", metavar="PASSWORD")
parser.add_option("-s", "--server", dest="serverfqdn", help="FQDN of satellite server - omit http://", metavar="SERVERFQDN")
(options, args) = parser.parse_args()

if not ( options.login and options.password and options.serverfqdn ):
	print "Must specify login, password and server options.  See usage:"
	parser.print_help()
	print "\nExample usage: ./satserver-listmachines.py -l bholden -p password -s satellite.example.com"
	sys.exit(1)
else:
	login = options.login
	password = options.password
	serverfqdn = options.serverfqdn

SATELLITE_URL = "http://%s/rpc/api" % serverfqdn
SATELLITE_LOGIN = login
SATELLITE_PASSWORD = password

try:
	client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
	key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)
except xmlrpclib.Fault,e:
	print "Could not connect to Satellite server.  Got exception:", e
	sys.exit(1)
except socket.error,e:
	print "Got Socket error:", e
	sys.exit(1)
except Exception, e:
	print "Got general exception", e
	sys.exit(1)

print "Getting satellite server statistics\n\n"
try:
	print "-----------------------\n"

	active_systems = client.system.list_user_systems(key)
	print "Active Systems: %i" % len(active_systems)
	for system in active_systems:
		print "\tSystem found was: %s" % system['name']

		cpu_type = client.system.getCpu(key, system['id'])
		print "\t\tCPU configuration is:"
		print "\t\t\t%s Step %s" % (cpu_type['model'], cpu_type['stepping'])
		print "\t\t\t%s Cache" % cpu_type['cache']

		memory_type = client.system.getMemory(key, system['id'])
		print "\t\tMemory configuration is:"
		print "\t\t\t%iMB Physical - %iMB Swap" % (memory_type['ram'], memory_type['swap'])

		dmi_type = client.system.getDmi(key, system['id'])
		print "\t\tDMI configuration is:"
		print "\t\t\tVendor is %s ; BIOS Vendor is %s ; BIOS version is %s " % (dmi_type['vendor'], dmi_type['bios_vendor'], dmi_type['bios_version'])
		
		basechan_info = client.system.getSubscribedBaseChannel(key, system['id'])
		print "\t\tBase channel subscription:"
		print "\t\t\tName is: %s" % basechan_info['name']
		print "\t\t\tLabel is: %s" % basechan_info['label']
		print "\t\t\tDescription is: %s" % basechan_info['channel_description']
		print "\t\t\tArchitecture is: %s" % basechan_info['arch_name']

	print "-----------------------\n"

	client.auth.logout(key)

except xmlrpclib.Fault, e:
	print "Got XMLRPC error:", e
	sys.exit(1)
except KeyboardInterrupt:
	print "Got Ctrl-C.  Exiting"
except Exception, e:
	print "Got a general error:", e


sys.exit(0)
