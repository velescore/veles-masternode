#!/bin/bash
easyrsa_install_ca() {
	## Prepare easy-rsa
	rm -r /usr/share/veles/easy-rsa > /dev/null
	make-cadir /usr/share/veles/easy-rsa
	ln -s /usr/share/veles/dist-rsa/build-key-auto /usr/share/veles/easy-rsa/
	ln -s /usr/share/veles/dist-rsa/build-key-server-auto /usr/share/veles/easy-rsa/

	# Prepare fresh vars file
	if [ ! -f /usr/share/veles/easy-rsa/vars ] && [ -f /usr/share/veles/easy-rsa/vars.example ]; then
		cp -a /usr/share/veles/easy-rsa/vars.example /usr/share/veles/easy-rsa/vars
	fi
	source install/easy-rsa/patch_vars.sh

	# Save current path and enter easy-rsa directory
	pwd=$(pwd)
        cd /usr/share/veles/easy-rsa

	# Prevent bug when default openssl.cnf is missing
	if [ ! -f /usr/share/veles/easy-rsa/openssl.cnf ]; then
		ln -s /usr/share/veles/easy-rsa/openssl-1.0.0.cnf /usr/share/veles/easy-rsa/openssl.cnf
	fi

	# Init easyrsa dir
	if [ -f "/usr/share/easy-rsa/easyrsa" ]; then	# Easyrsa 3.x
		./easyrsa init-pki
		echo veles | ./easyrsa --req-cn=veles build-ca nopass
		cp -av /usr/share/veles/dist-keys/ca.crt pki/ca.crt
		cp -av /usr/share/veles/dist-keys/ca.key pki/private/ca.key
	else						# Easyrsa 2.x
		source ./vars
		./clean-all
	fi
	if [ ! -d keys ]; then mkdir keys; fi
	cp -a /usr/share/veles/dist-keys/ca.crt keys/
	cp -a /usr/share/veles/dist-keys/ca.key keys/

	# Finally build the certificate
        echo "* Generating new OpenVPN certificate key pair ..."
        ./build-key-server-auto server
        cp -a keys/server* /etc/veles/vpn/keys/ || $(echo "Error: Failed to copy new OpenVPN certificate to its path" ; exit 1)

        echo "* Generating new stunnel certificate key pair ..."
        ./build-key-server-auto stunnel > /dev/null
        cp -a keys/stunnel* /etc/veles/vpn/keys/ || $(echo "Error: Failed to copy new stunnel certificate to its path" ; exit 1)

        # Installing CA
        echo "Installing CA certificate ..."
        cp -a /usr/share/veles/dist-keys/ca.crt /etc/veles/vpn/keys/

        # Generating DH key
	if [ -f "/usr/share/easy-rsa/easyrsa" ]; then        # Easyrsa 3.x
		./easyrsa gen-dh 2048
		cp pki/dh.pem /etc/veles/vpn/keys/dh2048.pem
        else						# Easyrsa 2.x
		./build-dh 2048
        	cp keys/dh2048.pem /etc/veles/vpn/keys/dh2048.pem
	fi

	# Restore current path
	cd "$pwd"
}

easyrsa_install_ca
