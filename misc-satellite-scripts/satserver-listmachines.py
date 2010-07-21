#!/usr/bin/env python

"""
 File: satserver-listmachines.py
 Author: Brent Holden <bholden@redhat.com>
 Version: 1.0.3
 Last Modified: November 20, 2009
 Description: Reporting script for satellite.  Also generates .csv file in same directory with information
Copyright 2008, Red Hat, Inc

Licensed under the GPLv2

"""

import csv
import xmlrpclib
import socket
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--login", dest="login", help="Login user for satellite", metavar="LOGIN")
parser.add_option("-p", "--password", dest="password", help="Password for specified user on satellite", metavar="PASSWORD")
parser.add_option("-s", "--server", dest="serverfqdn", help="FQDN of satellite server - omit https://", metavar="SERVERFQDN")
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

SATELLITE_URL = "https://%s/rpc/api" % serverfqdn
SATELLITE_LOGIN = login
SATELLITE_PASSWORD = password

try:
    csv_writer = csv.writer(open("satellite-hosts.csv", "wb"), delimiter=';',  quoting=csv.QUOTE_NONE)
#    csv_writer = csv.writer(open("satellite-hosts.csv", "wb"), dialect='excel')

    title_row = ['Hostname,CPU,Memory,Vendor,Arch,Base Channel,Type,Running Kernel']
    csv_writer.writerow(title_row)

    client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
    key = client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)

    print "Getting satellite server statistics\n"
    active_systems = client.system.listActiveSystems(key)
    print "Active Systems: %i\n" % len(active_systems)
    print "-----------------------\n"


    for system in active_systems:
        print "System found:"
        print "\tHostname: %s" % system['name']

        cpu_type = client.system.getCpu(key, system['id'])
        print "\tCPU configuration is: %s" % cpu_type['model']

        memory_type = client.system.getMemory(key, system['id'])
        print "\tMemory configuration is: %iMB" % (memory_type['ram'])

        try:
            dmi_type_info = client.system.getDmi(key, system['id'])
            if 'system' in dmi_type_info:
                vendor_type = dmi_type_info['system']
                print "\tVendor is: %s" % vendor_type
            else:
                vendor_type = ''
        except:
            vendor_type = ''
		
        basechan_info = client.system.getSubscribedBaseChannel(key, system['id'])
        print "\tArchitecture is: %s" % basechan_info['arch_name']
        print "\tBase channel subscription: %s" % basechan_info['label']
		
        # virtual or physical
        if (cpu_type['model'].find('QEMU') == 0) or (vendor_type.find('VMware') == 0):
            machine_type = 'virtual'
        else:
            machine_type = 'physical'
        print "\tMachine Type: %s" % machine_type

        try:
            running_kernel = client.system.getRunningKernel(key, system['id'])
        except:
            running_kernel = ''
        if running_kernel: print "\tRunning Kernel is: %s" % running_kernel

        host_row = ["%s,%s,%s,%s,%s,%s,%s,%s" % (system['name'], cpu_type['model'], memory_type['ram'], vendor_type, basechan_info['arch_name'], basechan_info['label'], machine_type, running_kernel)]
        csv_writer.writerow(host_row)

    print "-----------------------\n"

    client.auth.logout(key)

except xmlrpclib.Fault,e:
    print "Could not connect to Satellite server.  Got exception:", e
    sys.exit(1)
except socket.error,e:
    print "Got Socket error:", e
    sys.exit(1)
except KeyboardInterrupt:
    print "Got Ctrl-C.  Exiting"
except Exception, e:
    print "Got general exception", e
    sys.exit(1)

sys.exit(0)
