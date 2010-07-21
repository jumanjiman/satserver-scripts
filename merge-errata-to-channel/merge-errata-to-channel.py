#!/usr/bin/env python

"""

 Copyright (c) 2008 Red Hat, Inc.
 Permission is hereby granted, free of charge, to any person obtaining a copy 
 of this software and associated documentation files (the "Software"), to 
 deal in the Software without restriction, including without limitation the 
 rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
 sell copies of the Software, and to permit persons to whom the Software is 
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.

 File: merge-errata-to-channel.py
 Author: Brent Holden <bholden@redhat.com>
 Version: 1.0.1
 Last Modified: September 10, 2009
 Description: Simple script to take in two channels (orig and dest) and merge errata based on an end date

"""

import getpass
import socket
import sys
import time
import xmlrpclib
from optparse import OptionParser

SUPPORTED_SATELLITE_VERSION = '5.2.0'

def satelliteLogin(sat_login, sat_passwd, sat_fqdn):
    # input: string login, string passwd, string fqdn
    # returns: string session key

    sat_url = "https://%s/rpc/api" % sat_fqdn
    client = xmlrpclib.Server(sat_url, verbose=0)
    key = client.auth.login(sat_login, sat_passwd)

    return (client, key)

def satelliteLogout(client, key):
    # input: session key
    # returns: error value from logout

    return client.auth.logout(key)

def isSupported(client):
    # input: xmlrpc client, session key
    # returns: boolean for supported satellite version

    if client.api.systemVersion() >= SUPPORTED_SATELLITE_VERSION:
        return True

    return False

def mergeChannelErrata(client, key, origin_channel, dest_channel, start_date, end_date):
    resp = client.channel.software.mergeErrata(key, origin_channel, dest_channel, start_date, end_date)
    return resp

def main():
    SUCCESS = 0
    XMLRPCERR = 21
    UNSUPPORTED = 23
    SOCKERR = 27

    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", type="string", help="User login for satellite", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password", type="string", help="Password for specified user on satellite.  If password is not specified it is read in during execution", metavar="PASSWORD", default=None)
    parser.add_option("-s", "--server", dest="serverfqdn", type="string", help="FQDN of satellite server - omit https://", metavar="SERVERFQDN")
    parser.add_option("-o", "--origin", dest="origin", type="string", help="Specify the original channel label", metavar="ORIGIN", default=None)
    parser.add_option("-d", "--destination", dest="destination", type="string", help="Specify the destination channel label", metavar="DESTINATION", default=None)
    parser.add_option("-b", "--beginning", dest="beginning", type="string", help="Specify the beginning date.  Date is in ISO 8601 (e.g. 2009-09-09) [Default: 2000-01-01", metavar="BEGINNING", default='2000-01-01')
    parser.add_option("-e", "--end", dest="end", type="string", help="Specify the end date.  Date is in ISO 8601 (e.g. 2009-09-10 for Sept 10th, 2009)", metavar="END", default=None)

    (options, args) = parser.parse_args()

    if not ( options.username and options.serverfqdn and options.origin and options.destination and options.end ):
        print "Must specify login, server, origin, destination, and end date options.  See usage:"
        parser.print_help()
        print "\nExample usage:\n"
        print "To merge errata from Red Hat channel to custom channel up to date 2009-09-09:\n\t./merge-errata-to-channel.py -u admin -p password -s satellite.example.com -o rhel-x86_64-server-5 -d release-5-u1-server-x86_64 -e 2009-09-09"
        print ""
        return 100
    else:
        login = options.username
        serverfqdn = options.serverfqdn
        origin = options.origin
        destination = options.destination
        beginning = options.beginning
        end = options.end

    	if not options.password:
    		password = getpass.getpass("%s's password:" % login)
    	else:
    		password = options.password

    # login to the satellite to get our client obj and session key
    print "* Logging into RHN Satellite"
    try:
        (sat_client, sat_sessionkey) = satelliteLogin(login, password, serverfqdn)
    except (xmlrpclib.Fault,xmlrpclib.ProtocolError), e:
        print "!!! Got XMLRPC error !!!\n\t%s" % e
        print "!!! Check Satellite FQDN and login information; You can also look at /var/log/httpd/error_log on the Satellite for more info !!!"
        return XMLRPCERR
    except socket.error, e:
        print "!!! Got socket error !!!\n\n%s" % e
        print "!!! Could not connect to %s" % serverfqdn
        return SOCKERR

    # check to see if we're supported
    print "* Checking if Satellite supports necessary calls"
    try:
        if isSupported(sat_client):
            print "\tSupported version of Satellite"
        else:
            print "\n!!! Unsupported version of Satellite !!!\n!!! Requires Satellite >= v%s !!!" % SUPPORTED_SATELLITE_VERSION
            return UNSUPPORTED
    except xmlrpclib.Fault, e:
        print "!!! Got XMLRPC fault\n\t%s" % e
        return XMLRPCERR
	
    # build out that channel - we borrow the channel name from the manifest filename and prepend 'release'
    print "* Merging errata from %s to %s between dates %s and %s" % (origin, destination, beginning, end)
    try:
        mergeChannelErrata(sat_client, sat_sessionkey, origin, destination, beginning, end)
        print "\tErrata merged sucessfully"
    except xmlrpclib.Fault, e:
        print "!!! Got XMLRPC Fault !!!\n\t%s" % e
        return XMLRPCERR

    # log out of the satellite for good behavior
    print "* Logging out of the Satellite"
    try:
        satelliteLogout(sat_client, sat_sessionkey)
    except xmlrpclib.Fault, e:
        print "!!! Got XMLRPC fault !!!\n\t%s" % e
        return XMLRPCERR

    print "* Operation successful.  Check Satellite console"
    return SUCCESS

if __name__ == "__main__":
    retval = 1
    try:
        retval = main()
    except KeyboardInterrupt:
        print "!!! Caught Ctrl-C !!!"

    print "\nExiting."
    sys.exit(retval)
		
