#!/bin/bash
# Fetches the installator wizard and performs full Veles Masternode
# installation from this source directory

echo "Preparing the installation environment ..."
git clone https://github.com/AltcoinBaggins/masternode-installer2 /tmp/veles-masternode-installer
(export VELES_MN_SRC=$(dirname $0) ; cd /tmp/veles-masternode-installer && make install)
rm -rf /tmp/veles-masternode-installer
