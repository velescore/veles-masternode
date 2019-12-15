#!/bin/bash
# Makes snapshot from dev machine to files directory
export PACKAGE_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
export DATA_DIR="${PACKAGE_DIR}/data"
export ROOT_PREFIX=""
export DIST_PREFIX="${DATA_DIR}/dist"
export LOG_FILE="/tmp/velesmn-install.log"

show_logo() {
  echo " ____   ____     .__                _________                       
_\___\_/___/____ |  |   ____   _____\_   ___ \  ___________   ____  
\___________/__ \|  | _/ __ \ /  ___/    \  \/ /  _ \_  __ \_/ __ \ 
   \  Y  /\  ___/|  |_\  ___/ \___ \\     \___(  <_> )  | \/\  ___/ 
    \___/  \___  >____/\___  >____  >\______  /\____/|__|    \___  >
               \/          \/     \/        \/                   \/ "
}

show_help() {
  show_logo
  echo -e ${1}
  echo -e "\nUsage: install.sh [action]\n\nActions:"
  echo -e "install (default)\tinstall Veles Masternode onto this system,"
  echo -e "\t\t\treinstall or update existing installation"
  echo -e "version\t\t\tprint version number and exit"
  echo -e "help\t\t\tshow this help and exit"
}

show_intro() {
  show_logo
  echo "Starting Veles Masternode 2g Installator ..."
  sleep 1
}

if [ "$1" == "" ] || [ "$1" == "install" ]; then
  show_intro
  # Save current path, restore later
  PWD=$( pwd )
  cd ${DATA_DIR}
  ${PACKAGE_DIR}/bin/snapshot install
  cd ${PWD}
elif [ "$1" == "--help" ] || [ "$1" == "help" ]; then
  show_help

elif [ "$1" == "version" ] || [ "$1" == "--version" ]; then
  cat application/version.py | grep version | grep -v '"""'

else
  show_help "\nError: Unknown action: ${1}"
fi
