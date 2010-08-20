#!/bin/bash

channel="$1"
regex="$2"

# add child channel $1 to all systems whose profile
# name matches regex $2

for i in $(spacecmd system_list | grep "$2"); do
  spacecmd -y system_addchildchannel $i "${channel}"
done
