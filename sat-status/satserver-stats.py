#!/usr/bin/env python

"""
Authored by Brent Holden
Copyright 2008, Red Hat, Inc

Licensed under the GPLv2

$Id: satserver-stats.py 34 2008-08-01 09:34:05Z brent $

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
	print "\nExample usage: ./satserver-stats.py -l bholden -p password -s satellite.example.com"
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
	users = client.user.listUsers(key)
	print "Registered Users: %i" % len(users)
	for user in users:
		print "\tLogin: %s - Userid: %s" % (user['login'], user['id'])
	print "-----------------------\n"

	sys_channels = client.channel.listSoftwareChannels(key)
	print "Found active channels: %i" % len(sys_channels)
	for channel in sys_channels:
		errata_list_bychannel = client.channel.software.listErrata(key, channel['label'])
		print "\tFor channel %s found %i errata" % (channel['label'], len(errata_list_bychannel))

		for errata in errata_list_bychannel:
			print "\t\t%s: %s => %s : %s" % (errata['issue_date'], errata['advisory_type'], errata['advisory'], errata['synopsis'])
	print "-----------------------\n"

	active_systems = client.system.listActiveSystems(key)
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
		
		basechan_info = client.system.getSubscribedBaseChannel(key, system['id'])
#		print basechan_info
		print "\t\tBase channel subscription:"
		print "\t\t\tName is: %s" % basechan_info['name']
		print "\t\t\tLabel is: %s" % basechan_info['label']
		print "\t\t\tDescription is: %s" % basechan_info['channel_description']
		print "\t\t\tArchitecture is: %s" % basechan_info['arch_name']

		childchans = client.system.listSubscribedChildChannels(key, system['id'])
		for child in childchans:
#			print child
			print "\t\tChild Channel subscription:"
			print "\t\t\tName is: %s" % child['name']
			print "\t\t\tLabel is: %s" % child['label']
			print "\t\t\tSummary is: %s" % child['summary']
		
		print ""

		upgd_pkgs = client.system.listLatestUpgradablePackages(key, system['id'])
		if len(upgd_pkgs) > 0: print "\t\tFound upgradable packages"
		for pkg in upgd_pkgs:
#			print pkg
			print "\t\t\tUpgradable package: %s : From version %s%s to %s%s" % (pkg['name'], pkg['from_version'], pkg['from_release'], pkg['to_version'], pkg['to_release'])
	print "-----------------------\n"

	list = client.channel.software.listPackagesWithoutChannel(key)
	print "Orphaned packages: %i" % len(list)
	for item in list:
		print "\tPackage found was: %s-%s%s" % (item['name'], item['version'], item['release'])
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
