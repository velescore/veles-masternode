#!/bin/bash
# Makes snapshot from dev machine to files directory
ROOT_PREFIX=""	# could be "" for /, "/srv", "/var/local" ...
DEST_PREFIX="/root/veles-masternode/dist"

while read path; do
	if [ -d "${ROOT_PREFIX}${path}" ]; then
		mkdir -p "${DEST_PREFIX}${path}" > /dev/null
		cp -auv "${ROOT_PREFIX}${path}/" $(dirname "${DEST_PREFIX}${path}/")
	else
		mkdir -p $(dirname "${DEST_PREFIX}${path}") > /dev/null
		cp -auv "${ROOT_PREFIX}${path}" $(dirname "${DEST_PREFIX}${path}")
	fi
done < snapshot.list

while read path; do
	mkdir -p "${DEST_PREFIX}${path}" &> /dev/null
done < empty-dirs.list


