#!/bin/bash
echo -e "Preparing Veles Masternode installation ...\n"
echo -n "* Checking whether netstat command is present ... "

if command -v netstat >/dev/null 2>&1; then
  echo "yes"
else
  echo "no"
  apt-get update
  apt-get install make
fi

cd $(dirname $0)
make install
