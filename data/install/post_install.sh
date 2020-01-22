#!/bin/bash
do_post_install() {
	pwd=$(pwd)

	## Create symlinks
	echo "* Creating symlinks ..."
	if [ -f "/var/lib/veles/wallet/veles.conf" ]; then
		mv "/var/lib/veles/wallet/veles.conf" "/var/lib/veles/wallet/veles.conf.backup"
	fi
	if [ ! -d /root/.veles ]; then
		mkdir /root/.veles
	fi
	ln -s "/etc/veles/veles.conf" "/var/lib/veles/wallet/veles.conf"
	ln -s "/etc/veles/veles.conf" "/root/.veles/veles.conf"
	touch /var/lib/veles/wallet/debug.log
	ln -s "/var/lib/veles/wallet/debug.log" "/var/log/veles/debug.log"

	## Update systemd resolver configuration
	if [ -f /etc/systemd/resolved.conf ]; then
		echo "Note: /etc/systemd/resolved.conf not present"

		# Add fallback DNS servers in case of local resoliton fails
		sed -i 's/#FallbackDNS=/FallbackDNS=1.1.1.1 8.8.8.8 1.0.0.1 8.8.4.4 /g' /etc/systemd/resolved.conf

		# Make sure we reload systemd resolver settings
		systemctl daemon-reload
		systemctl restart systemd-resolved
	fi

	## Update netfilter and ufw rules
	# Packet forwarding
	sed -i 's/^[# ]*net.ipv4.ip_forward=.*$//g' /etc/sysctl.conf
	echo -e '\n# Added for Veles Core dVPN\nnet.ipv4.ip_forward=1' >> /etc/sysctl.conf
	sysctl -p

	# Ufw config update for packet forwarding
	sed -i 's/^[# ]*DEFAULT_FORWARD_POLICY=.*$/# Updated for Veles Core dVPN: ACCEPT\nDEFAULT_FORWARD_POLICY="ACCEPT"/g' /etc/default/ufw

	# Open neccessary ports
	#ufw allow 22/tcp comment 'SSH [added by Veles MN]'	# done when service gets installed
	# TODO: use ports conf or such source
	ufw allow 53/tcp comment 'Veles Masternode dVPN: DNS'
	ufw allow 53/udp comment 'Veles Masternode dVPN: DNS'
	ufw allow 443/tcp comment 'Veles Masternode dVPN: HTTPS/multiprotocol'
	ufw allow 443/udp comment 'Veles Masternode dVPN: HTTPS/multiprotocol'
	ufw allow 21337/tcp comment 'Veles Masternode dVPN: Veles Core node'
	ufw allow 21344 comment 'Veles Masternode dVPN: shadowsocks'

	# Masquerade
	pub_iface=$(ip route | grep default | awk '{print $5}')
	if ! grep "\-A POSTROUTING \-s 10\." /etc/ufw/before.rules | grep " \-j MASQUERADE" > /dev/null; then
		sed -i "s/*filter$/\n# Added for Veles Code dVPN\n*nat\n:POSTROUTING ACCEPT [0:0]\n-A POSTROUTING -s 10.100.0.0\/8 -o ${pub_iface} -j MASQUERADE\nCOMMIT\n\n# Don't delete these required lines, otherwise there will be errors\n*filter/g" /etc/ufw/before.rules
	fi
	
	# Reload ufw
	ufw disable
	yes | ufw enable

	## Update config
        # If MN key is not set, disable it for now
        if grep MASTERNODE_KEY_UNSET /etc/veles/veles.conf > /dev/null; then
                sed -i "s/masternodeprivkey=/#masternodeprivkey=/g" /etc/veles/veles.conf
                sed -i "s/masternode=1/#masternode=0/g" /etc/veles/veles.conf
        fi
        # If signing key is not set, disable it for now
        if grep SIGNING_KEY_UNSET /etc/veles/mn.conf > /dev/null; then
                sed -i "s/signing_key=/#signing_key=/g" /etc/veles/mn.conf
        fi

        ## Install Veles CA, generate and copy server certificates
	source install/easy-rsa/install_ca.sh

	# Restore current path, just for case
	cd "$pwd"
}
