#!/bin/bash
# Veles Core Masternode installation launcher (2nd gen, experimental)
# Fetches the installator wizard and performs full Veles Masternode
# installation from this source directory

if [[ "${1}" == "--help" ]]; then
  echo "
Veles Core Masternode installation launcher (2nd gen, experimental)
 ____   ____     .__                _________
_\___\_/___/____ |  |   ____   _____\_   ___ \  ___________   ____  
\___________/__ \|  | _/ __ \ /  ___/    \  \/ /  _ \_  __ \_/ __ \ 
   \  Y  /\  ___/|  |_\  ___/ \___ \\     \___(  <_> )  | \/\  ___/ 
    \___/  \___  >____/\___  >____  >\______  /\____/|__|    \___  >
               \/          \/     \/        \/                   \/ 

Usage:  install.sh [options]
Starts an installation process of the Veles Core Masternode

Options:
  --non-interactive         perform fully automatic installation
  --docker-test             install from docker and run all tests
"
  exit 0;
fi

echo "Downloading Veles Masternode installer wizard ..."
git clone https://github.com/AltcoinBaggins/masternode-installer2 /tmp/veles-masternode-installer
(export VELES_MN_SRC=$(dirname $0) ; /tmp/veles-masternode-installer/install.sh "${0}")
rm -rf /tmp/veles-masternode-installer

