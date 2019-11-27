#!/bin/bash
# Makes snapshot from dev machine to files directory
ROOT_PREFIX=""	# could be "" for /, "/srv", "/var/local" ...
DIST_PREFIX="/root/veles-masternode/dist"
DIST_OVER_PREFIX="/root/veles-masternode/dist-overlay"

replace_ports() {
        while read line; do
		port=$(echo $line | awk '{print $1}')
		service=$(echo $line | awk '{print $2}')

		if $(echo $line | grep -v '#' > /dev/null); then	# just ignore whole line if comment is present
			find "${DIST_PREFIX}" -type f -iname "*.*" -exec sed -i "s/${port}/{{svc-port:${service}}}/" "{}" +;
		fi
        done < ports.cf
}

undo_replace_ports() {
        while read line; do
		port=$(echo $line | awk '{print $1}')
		service=$(echo $line | awk '{print $2}')

		if $(echo $line | grep -v '#' > /dev/null); then	# just ignore whole line if comment is present
			find "${DIST_PREFIX}" -type f -iname "*.*" -exec sed -i "s/{{svc-port:${service}}}/${port}/" "{}" +;
		fi
        done < ports.cf
}

replace_vars() {
        while read line; do
		name=$(echo $line | awk '{print $1}')
		value=$(echo $line | awk '{print $2}')

		if $(echo $line | grep -v '#' > /dev/null); then	# just ignore whole line if comment is present
			find "${DIST_PREFIX}" -type f -iname "*.*" -exec sed -i "s/{{${name}}}/${value}/" "{}" +;
		fi
        done < vars.cf
}

undo_replace_vars() {
        while read line; do
		name=$(echo $line | awk '{print $1}')
		value=$(echo $line | awk '{print $2}')

		if $(echo $line | grep -v '#' > /dev/null); then	# just ignore whole line if comment is present
			find "${DIST_PREFIX}" -type f -iname "*.*" -exec sed -i "s/${value}/{{${name}}}/" "{}" +;
		fi
        done < vars.cf
}


mn_backup() {
	copy_snapshot "${ROOT_PREFIX}" "${DIST_PREFIX}" "backup"
	replace_ports
}

mn_restore() {
	copy_snapshot "${DIST_PREFIX}" "${ROOT_PREFIX}" "restore"
}

copy_snapshot() {
	src_prefix="${1}"
	dst_prefix="${2}"

	while read path; do
		if [ -d "${src_prefix}${path}" ]; then
			mkdir -p "${dst_prefix}${path}" > /dev/null
			cp -auv "${src_prefix}${path}/" $(dirname "${dst_prefix}${path}/")
		else
			mkdir -p $(dirname "${dst_prefix}${path}") > /dev/null
			cp -auv "${src_prefix}${path}" $(dirname "${dst_prefix}${path}")
		fi
	done < snapshot.list

	while read path; do
		mkdir -p "${dst_prefix}${path}" &> /dev/null
	done < empty-dirs.list
}


if [ "$#" -ne 1 ] || [ "$1" == "--help" ]; then
	echo -e "Usage: snapshot.sh [action]\n\nActions:"
	echo -e "restore\t\trestores mn system snapshot to local system"
	echo -e "backup\t\tbacks up a snapshot of mn system from local system"

elif [ "$1" == "restore" ]; then
	mn_restore

elif [ "$1" == "unparse_ports" ]; then
	replace_ports

elif [ "$1" == "parse_ports" ]; then
	undo_replace_ports

elif [ "$1" == "parse_vars" ]; then
	replace_vars

elif [ "$1" == "unparse_vars" ]; then
	undo_replace_vars

else
	mn_backup
fi
