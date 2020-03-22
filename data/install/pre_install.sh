#!/bin/bash
do_pre_install() {
  # Cleaning up. Could be removed few versions later after 1.99.05, 
  # but for now always remove the files of the old version
	rm -r ${DIST_PREFIX}/usr/lib/veles/masternode
}
