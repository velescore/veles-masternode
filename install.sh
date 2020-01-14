#!/bin/bash
echo -e "Preparing Veles Masternode installation ...\n"
echo -n "* Checking whether make command is present ... "

if command -v make >/dev/null 2>&1; then
  echo "yes"
else
  echo "no"
  apt-get update
  apt-get install -yq make
fi

cd $(dirname $0)

if [[ "${1}" == "--non-interactive" ]]; then
  make auto_install
elif [[ "${1}" == "--docker-test" ]]; then
  make docker_test_all
else
  make install
fi

