#!/bin/bash

# Written by Brent Holden (bholden@redhat.com)
# Copyright 2008 - Red Hat, Inc
#
# Licensed under the GPLv2
#
# USAGE: 
# Contents of channel file has each channel-label to synchronize on a new line
# cat channel-file | xargs ./chansync.sh


LOGFILE="chansync.log"
SYNC_COMMAND="satellite-sync"
OPTS=""
CHANNELS=""

if [ -z $1 ]
then 
	echo "usage ./chansync.sh CHANNEL1 CHANNEL2 ..."
	echo ""
	echo "This utility continues with the satellite sync if it dumps out due to a timeout/XMLRPC error."
	exit 0
fi

# Execute rest of script logging to file $LOGFILE
exec > $LOGFILE 2>&1


# Loop through our argument list and append each channel separated by -c
while [ $# -ne 0  ]
do
	CHANNELS="$CHANNELS -c $1"
	shift
done

# Define our command including channel options
COMMAND="$SYNC_COMMAND $OPTS $CHANNELS"
STAT=1

# Now loop through until we get a clean exit status
while [ $STAT -ne 0 ]
do
	$COMMAND
	STAT=$?

	# Conditional check and breakout if channels dont exist
	if [ $STAT -eq 12 ]; then
		echo "Some channels specified do not exist.  Unable to continue"
		echo "Passed in: $CHANNELS"
		break
	else
		continue
	fi
done

DATE=`date`
echo "Exiting: $DATE"
exit 0
