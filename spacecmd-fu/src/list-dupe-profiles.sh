#!/bin/bash

# Find duplicate system entries easily

for i in $(spacecmd system_list); do
  spacecmd system_details $i | grep WARNING
done
