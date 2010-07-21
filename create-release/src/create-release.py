#!/usr/bin/env python

"""
 File: create-release.py
 Author: Brent Holden <bholden@redhat.com>
 Version: 1.3
 Last Modified: September 23, 2009
 Description: Based on create-channel-to-update by Justin Sherrill
"""

import getpass
import math
import os.path
import re
import socket
import sys
import time
import xmlrpclib
from optparse import OptionParser

SUPPORTED_SATELLITE_VERSION_MIN = '5.1.0'
SUPPORTED_ARCHES = { 'i386':'IA-32', 'x86_64':'x86_64', 's390':'s390x', 's390x':'s390x', 'ia64':'IA-64', 'ppc':'PPC', 'ppc64':'PPC', 'noarch':'NOARCH' }
RETURN_VAL = {'SUCCESS':0, 'FILEERR':20, 'XMLRPCERR':21, 'PKGSNOTFOUND':22, 'UNSUPPORTED':23, 'NOARCHFOUND':24, 'TOOMANYARCHES':25, 'NOBASECHAN':26, 'SOCKERR':27, 'USAGE':100 }

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

    if client.api.systemVersion() >= SUPPORTED_SATELLITE_VERSION_MIN:
        return True
    else:
        return False

def findChannelArch(client, key, arch):
    # input: xmlrpc client, session key, string arch to look for
    # returns: string channel arch grabbed from satellite

    return_arch = None

    for ar in client.channel.software.listArches(key):
        if ar['name'] == arch:
            return_arch = ar['label']

    return return_arch

def findPackageIDs(client, key, pkgs_from_manifest, release_pkgs_arch, redhat_only=True):
    # input: xmlrpc client, session key, string array of pkgs from manifest, string of arch
    # returns: int array of pkg ids found , string array pkg names not found, array of channels packages were found in

    satellite_pkgs_onfile = {}
    pkg_ids_to_add = []
    pkgs_notfound = []
    channels_pkgs_found_in = []

    if redhat_only:
        channels_to_look_in = client.channel.listRedHatChannels(key)
    else:
        channels_to_look_in = client.channel.listSoftwareChannels(key)

    for chan in channels_to_look_in:
        if len(pkgs_from_manifest) > 0: # keep going if there are still packages in the manifest
            if client.channel.software.getDetails(key, chan['label'])['arch_name'] == release_pkgs_arch:
                print "\tScanning channel:", chan['label']
                for pkg in client.channel.software.listAllPackages(key, chan['label']):
                    current_package = "%s-%s-%s.%s" % (pkg['name'], pkg['version'], pkg['release'], pkg['arch_label'])
                    if current_package in pkgs_from_manifest:
                        pkg_ids_to_add.append(pkg['id'])
                        pkgs_from_manifest.remove(current_package)
                        if chan['label'] not in channels_pkgs_found_in: channels_pkgs_found_in.append(chan['label'])

    pkgs_notfound = pkgs_from_manifest

    print ""
    print "\tFound %i packages to put into channel" % len(pkg_ids_to_add)
    print "\tFound %i missing packages:" % len(pkgs_notfound)
    print "\tPackages found in channel labels:"
    for i in channels_pkgs_found_in:
        print "\t\t%s" % i

    return (pkg_ids_to_add, pkgs_notfound, channels_pkgs_found_in)

def addPkgsToChannel(client, key, label, pkg_ids_to_add, chunk):
    # input: xmlrpc client, session key, string channel label, integer array of pkg ids to add
    # returns: boolean of success.  if there's a failure it will raise an exception (xmlrpclib.Fault)

    # split array function shamelessly borrowed from ruby
    split_array = lambda v, l: [v[i*l:(i+1)*l] for i in range(int(math.ceil(len(v)/float(l))))]

    print "\tSplitting package array into chunks"
    splitup_pkg_arrays = split_array(pkg_ids_to_add, chunk)

    # we add packages in array chunks because larger arrays cause satellite to hang on a 502 proxy error
    for index, pkg_ar in enumerate(splitup_pkg_arrays):
        retries = 3
        while retries > 0:
            try:
                print "\tAdding chunk %i / %i ..." % (index+1, len(splitup_pkg_arrays)),
                sys.stdout.flush()
                client.channel.software.addPackages(key, label, pkg_ar)
                print "Done"
                # reset the retry counter
                retries = 0
            except xmlrpclib.Fault, e:
                retries -= 1
                print "\t! Got XMLRPC failure: %s ; Retries left %i" % (e, retries)
				
                # sleep for 5s
                if retries != 0:
                    print "\tSleeping for 5 seconds between retries"
                    time.sleep(5)
                else:
                    print "\t! Exceeded retries due to XMLRPC failures.  Skipping this chunk"
            except xmlrpclib.ProtocolError, e:
                retries -= 1
                print "\t! Got XMLRPC failure: %s ; Retries left %i" % (e, retries)
                print "\t! Check apache error log on server.  Likely caught a bug with Tomcat's mod_proxy"
                print "\t! Try again with a smaller chunksize"

                # sleep for 5s
                if retries != 0:
                    print "\tSleeping for 5 seconds between retries"
                    time.sleep(5)
                else:
                    print "\t! Exceeded retries due to XMLRPC failures.  Skipping this chunk"

    return True

def cloneSoftwareChannel(client, key, orig_channel_label, label, desc, parent):
    # input: xmlrpc client, session key, string channel label, string channel desc, string channel parent
    # returns: integer of channel created by channel.software.clone (1)

    # create software channel
    if parent is not '':
        clone_channel_details = {'name': label, 'label':label, 'summary':desc, 'parent_channel':parent}
    else:
        clone_channel_details = {'name': label, 'label':label, 'summary':desc}
    return client.channel.software.clone(key, orig_channel_label, clone_channel_details, True)

def createSoftwareChannel(client, key, label, desc, arch, parent=''):
    # input: xmlrpc client, session key, string channel label, string channel desc, string channel arch, string channel parent
    # returns: integer of channel created by channel.software.create (1)

    # create software channel
    return client.channel.software.create(key, label, label, desc, arch, parent)

def deleteSoftwareChannel(client, key, label):
    # input: xmlrpc client, session key, string channel label
    # returns: success value of channel.software.delete

    # create software channel
    return client.channel.software.delete(key, label)

def doesParentChannelExist(client, key, parent, arch):
    # input: xmlrpc client, session key, string parent channel label
    # returns: boolean true or false if it exists or not

    for chan in client.channel.listSoftwareChannels(key):
        if (chan['label'] == parent) and (chan['parent_label'] == '') and (chan['arch'] == arch):
            return True
    return False

def readManifest(manifest_file):
    # input: string array package manifest, string arch
    # returns: array of strings of rpms in manifest, array of strings of arches

    pkgs = []
    arches_found = []

    # open the file and read it into an array while removing the .rpm extension
    f = open(manifest_file)
    for line in f.readlines():
        result = re.sub(r'\.rpm','',line)
        pkgs.append(result.rstrip())

        try:
            pkg_arch = line.split('.')[-2] 
        except IndexError:
            pkg_arch = None
        
        if pkg_arch in SUPPORTED_ARCHES:
            if SUPPORTED_ARCHES[pkg_arch] not in arches_found:
                arches_found.append(SUPPORTED_ARCHES[pkg_arch])
    f.close()
    return (pkgs, arches_found)

def parseArguments(help=False):
    # input: boolean to show help
    # returns: True if help is printed, otherwise return parser.parse_args struct
    
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", type="string", help="User login for satellite", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password", type="string", help="Password for specified user on satellite.  If password is not specified it is read in during execution", metavar="PASSWORD", default=None)
    parser.add_option("-s", "--server", dest="serverfqdn", type="string", help="FQDN of satellite server - omit https://", metavar="SERVERFQDN")
    parser.add_option("-f", "--file", dest="profile", type="string", help="Specify the file containing the RPM manifest", metavar="PROFILE")
    parser.add_option("-c", "--chunk", dest="chunk", type="int", help="Specify the chunk size of RPM channel additions (Default: 150)", metavar="CHUNK", default=150)
    parser.add_option("-b", "--base", dest="base", type="string", help="Specify the base channel (parent) the manifest will be imported under (Default: None)", metavar="BASE", default='')
    parser.add_option("-n", "--name", dest="name", type="string", help="Specify the channel name.  (Default: profile file name)", metavar="NAME", default=None)
    parser.add_option("-r", "--redhat-only", action="store_true", dest="search_redhat_only", help="Search Red Hat Channels only (Satellite v5.3 and above  (Default: False)", metavar="SEARCH_REDHAT_ONLY", default=False)
    parser.add_option("-L", "--clone", action="store_true", dest="clone", help="Force channel cloning; operation default is to create (Default: False)", metavar="CLONE", default=False)
    parser.add_option("-d", "--delete", action="store_true", dest="delete", help="Attempt channel deletion before creation (Default: False)", metavar="DELETE", default=False)

    if help:
        parser.print_help()
        return True
    else:
        return parser.parse_args()

def validateArguments(options):
    # input: options variable pulled from parseArguments()
    # returns: False if arguments do not validate, otherwise it returns a tuple of username, password, serverfqdn, profile, chunk, base, name, search_redhat_only
    
    # do some checks to make sure all the arguments are there
    if not ( options.username and options.serverfqdn and options.profile ):
        print "Must specify login, password and server options.  See usage:"
        parseArguments(help=True)
        print "\nExample usage:\n"
        print "To create a new base channel from a profile:\n\t./create-release.py -u admin -p password -s satellite.example.com -f data/5-U1-Server-i386"
        print ""
        print "To create a new child channel from a profile under a specified base channel:\n\t./create-release.py -u admin -p password -s satellite.example.com -b release-5-u3-server-x86_64 -f data/5-U3-Server-x86_64-VT"
        return False
    else:
        return (options.username, options.password, options.serverfqdn, options.profile, options.chunk, options.base, options.name, options.search_redhat_only, options.clone, options.delete)

def main():
    # parse arguments from the command line
    (options, args) = parseArguments()

    # validate arguments for correctness
    validation = validateArguments(options)
    if validation is False:
        return RETURN_VAL['USAGE']
    else:
        (login, password, serverfqdn, profile, chunk_size, parent_channel, channel_name, search_redhat_only, clone, delete) = validation
    
    if not password: password = getpass.getpass("%s's password:" % login)

    if not channel_name:
        channel_label = "release-" + os.path.basename(profile).lower()
    else:
        channel_label = channel_name

    # read in manifest file
    print "* Reading in manifest profile"
    try:
        (manifest_pkgs, manifest_arch) = readManifest(profile)
    except IOError:
        print "Could not find manifest file.  Exiting"
        return RETURN_VAL['FILEERR']

    # include some logic to check the manifest architecture
    if len(manifest_arch) == 0:
        print "! No architectures found to import"
        return RETURN_VAL['NOARCHFOUND']

    # determine if there are too many arches in the list
    simple_arch_list = list(set(manifest_arch))
    if ('NOARCH' in simple_arch_list): simple_arch_list.remove('NOARCH')
    if ('IA-32' in simple_arch_list) and ('x86_64' in simple_arch_list): simple_arch_list.remove('IA-32')

    if len(simple_arch_list) > 1:
        print "! More than one Arch found in manifest\n\tFound %s" % manifest_arch
        print "! Can only import one architecture for a given manifest"
        return RETURN_VAL['TOOMANYARCHES']

    print "* Arch determined to be %s" % simple_arch_list[0]

    try:    # top level try to catch all xmlrpc and socket errors

        # login to the satellite to get our client obj and session key
        print "* Logging into RHN Satellite"
        (sat_client, sat_sessionkey) = satelliteLogin(login, password, serverfqdn)

        # check to see if we're supported
        print "* Checking if Satellite supports necessary calls"
        if isSupported(sat_client):
            print "\tSupported version of Satellite"
        else:
            print "\n! Unsupported version of Satellite\n! Requires Satellite >= v%s" % SUPPORTED_SATELLITE_VERSION_MIN
            return RETURN_VAL['UNSUPPORTED']

        # make sure if we're trying to create under a base channel that it exists and supports our arch
        # this will also fail if we try and create as a child to an existing child channel
        if parent_channel is not '':
            print "* Trying to find base channel %s specified" % parent_channel
            if doesParentChannelExist(sat_client, sat_sessionkey, parent_channel, simple_arch_list[0]):
                print "\tFound base channel %s" % parent_channel
                print "\tUsing base channel %s" % parent_channel
            else:
                print "! Cannot use base channel %s .  Check label and arch" % parent_channel
                return RETURN_VAL['NOBASECHAN']

        # find the IDs for packages listed in the manifest
        print "* Searching channels on Satellite for package ids matching manifest"
        (pkg_ids, pkg_notfound, channels_found_in) = findPackageIDs(sat_client, sat_sessionkey, manifest_pkgs, simple_arch_list[0], search_redhat_only)

        if len(pkg_notfound) > 0:
            print "\n! Could not create channel ; Following %i pkgs not found on Satellite:" % len(pkg_notfound)
            for pk in pkg_notfound:
                print "\t%s" % pk
            return RETURN_VAL['PKGSNOTFOUND']

        # try and delete the channel before creation
        if delete:
            print "* Attempting to delete channel: %s" % channel_label
            deleteSoftwareChannel(sat_client, sat_sessionkey, channel_label)
	
        # build out that channel - we borrow the channel name from the manifest filename and prepend 'release' ; clone by default
        print "* Creating software channel from profile"
        if clone and len(channels_found_in) == 1:
            cloneSoftwareChannel(sat_client, sat_sessionkey, channels_found_in[0], channel_label, channel_label, parent_channel)
        else:
            createSoftwareChannel(sat_client, sat_sessionkey, channel_label, channel_label, findChannelArch(sat_client, sat_sessionkey, simple_arch_list[0]), parent_channel)

        print "\tChannel created sucessfully"

        # add in the packages as long as we have all of them available to put into the channel
        print "* Adding packages to software channel"
        addPkgsToChannel(sat_client, sat_sessionkey, channel_label, pkg_ids, chunk_size)
		
    	# log out of the satellite for good behavior
        print "* Logging out of the Satellite"
        satelliteLogout(sat_client, sat_sessionkey)

    except (xmlrpclib.Fault,xmlrpclib.ProtocolError), e:
        print "! Got XMLRPC error\n\t%s" % e
        print "! Check Satellite logs : /var/log/rhn/rhn_web_api.log"
        return RETURN_VAL['XMLRPCERR']
    except socket.error, e:
        print "! Got socket error\n\n%s" % e
        print "! Could not connect to %s" % serverfqdn
        return RETURN_VAL['SOCKERR']

    print "* Operation successful.  Check Satellite console"
    return RETURN_VAL['SUCCESS']

if __name__ == "__main__":
    retval = 1
    try:
        retval = main()
    except KeyboardInterrupt:
        print "! Caught Ctrl-C"

    print "\nExiting."
    sys.exit(retval)
