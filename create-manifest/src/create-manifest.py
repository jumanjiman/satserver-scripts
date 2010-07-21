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

 File: create-manifest.py
 Author: Brent Holden <bholden@redhat.com>
 Version: 1.0
 Last Modified: February 19, 2009
 Description: Reads the RPM database and creates a manifest from the installed list

"""

import os
import rpm
import sys
from optparse import OptionParser

def main():
	parser = OptionParser()
	parser.add_option("-f", "--filename", dest="filename", default="MANIFEST", help="Manifest filename (Default: manifest)", metavar="FILENAME")
	(options, args) = parser.parse_args()

	try:
		manifest_fd = open(options.filename, 'w')
	except OSError, e:
		print "Got an OS error: %s \nExiting."
		return 1

	print "Capturing local RPM database"
	trans_set = rpm.ts()
	matches = trans_set.dbMatch()

	for header in matches:
	        manifest_fd.write("%s-%s-%s.%s.rpm\n" % (header['name'], header['version'], header['release'], header['arch']))

	manifest_fd.close()

	return 0


if __name__ == "__main__":
	retval = 1
	try:
		retval = main()
	except KeyboardInterrupt:
		print "!!! Caught Ctrl-C !!!"

	print "\nExiting."
	sys.exit(retval)
		
