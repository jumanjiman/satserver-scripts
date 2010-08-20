#!/bin/bash

# usage: systems_with_pkg.sh [name-of-pkg]
# example
#   systems_with_pkg.sh crontabs
#

for i in $(spacecmd system_list); do
  echo -n $i " "
  spacecmd system_listinstalledpackages $i |grep $1
done
