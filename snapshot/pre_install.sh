#!/bin/bash
do_pre_install() {
	# Save current path
	pwd=$(pwd)

	# Cleaning up
	rm -r ${DIST_PREFIX}/usr/lib/veles/masternode

	# If MN key is not set, disable it for now
	if grep MASTERNODE_KEY_UNSET ${DIST_PREFIX}/etc/veles/veles.conf > /dev/null; then
		sed -i "s/masternodeprivkey=/#masternodeprivkey=/g" ${DIST_PREFIX}/etc/veles/veles.conf
		sed -i "s/masternode=1/#masternode=0/g" ${DIST_PREFIX}/etc/veles/veles.conf
	fi

	# Generate and copy server certificate
	echo "* Generating new OpenVPN certificate key pair ..."
	cd ${DIST_PREFIX}/usr/share/veles/easy-rsa
	rm keys/* > /dev/null ; cp -av dist-keys/* keys/
	./build-key-server-auto server > /dev/null
	cp -av keys/server* ${DIST_PREFIX}/etc/veles/vpn/keys/ || $(echo "Error: Failed to copy new OpenVPN certificate to its path" ; exit 1)
	echo "* Generating new OpenVPN certificate key pair ..."
	cd ${DIST_PREFIX}/usr/share/veles/easy-rsa && ./build-key-server-auto stunnel > /dev/null
	cp -av keys/stunnel* ${DIST_PREFIX}/etc/veles/vpn/keys/ || $(echo "Error: Failed to copy new stunnel certificate to its path" ; exit 1)

	# Installing CA
	echo "Installing CA certificate ..."
	cp -av keys/ca.crt ${DIST_PREFIX}/etc/veles/vpn/keys/

	# Generating DH key
	./build-dh 2048
	cp keys/dh2048.pem /etc/veles/vpn/keys/

	# Restore current path
	cd "$pwd"
}
