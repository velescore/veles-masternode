#!/bin/bash
do_post_install() {
	# Save current path
	pwd=$(pwd)

	# Creating symlinks
	echo "* Creating symlinks ..."
	echo "${ROOT_PREFIX}/etc/veles/veles.conf => ${DIST_PREFIX}/var/lib/veles/wallet/veles.conf"
	rm "${DIST_PREFIX}/var/lib/veles/wallet/veles.conf" > /dev/null ; ln -s "${ROOT_PREFIX}/etc/veles/veles.conf" "${DIST_PREFIX}/var/lib/veles/wallet/veles.conf"

	# Restore current path
	cd "$pwd"
}
