#!/bin/bash

# Find duplicate system entries easily

for i in $(spacecmd system_list); do
  spacecmd system_details $i | grep WARNING
done

## -- Returns output like:
# WARNING: Multiple systems found with the same name
# WARNING: id-rhds01 = 1000017547
# WARNING: id-rhds01 = 1000017567
# WARNING: id-rhds01 = 1000017587
# WARNING: Multiple systems found with the same name
# WARNING: ob-gts01.test.ise.com = 1000014690
# WARNING: ob-gts01.test.ise.com = 1000017467
