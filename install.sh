#!/bin/bash

echo "Preparing the installation environment ..."
git clone https://github.com/AltcoinBaggins/masternode-installer2 /tmp/veles-masternode-installer
(cd /tmp/veles-masternode-installer && make install)
rm -rf /tmp/veles-masternode-installer