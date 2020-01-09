#!/bin/bash
echo "Warning: Installation by calling install.sh is deprecated and will be removed in next version."
echo "New installation method: make install"
echo -n "Starting in 5 seconds "
sleep 1 ; echo -n "." ; sleep 1 ; echo -n "." ; sleep 1 ; echo -n "." ; echo -n "." ; sleep 1 ; echo -n "." ;
cd $(dirname $0)
make install
