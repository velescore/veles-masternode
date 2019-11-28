#!/bin/bash
# Commandline pre-install configuration wizard
# for Veles Masternode

# Test an IP address for validity:
# Usage:
#      valid_ip IP_ADDRESS
#      if [[ $? -eq 0 ]]; then echo good; else echo bad; fi
#   OR
#      if valid_ip IP_ADDRESS; then echo good; else echo bad; fi
#
MN_VERSION="1.99.03"
CORE_VERSION="0.18.1.3"
BACKTITLE="Veles Core Masternode Installation"	# ${MN_VERSION}/${CORE_VERSION}"
TITLE="Veles Core Masternode"
WALLET_DIR="/var/lib/veles/wallet"
BACKUP_DIR="/var/lib/veles/wallet.backup"

function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

install_dialog_deps() {
	if ! dpkg --get-selections | grep "dialog" > /dev/null; then
		echo " * Installing dependencies of the installator ..."
		apt-get install --no-install-recommends -y dialog
	fi
}

#fetch_mn_state() {
#	veles-cli masternode status | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])"
#}

check_mn_key() {
	mnkey="${1}"
	length=${#mnkey}

	[ $length -gt 48 ] && [ $length -lt 65 ] && return 0 || return 1     # TODO: better mn key validity checks
}

find_mn_key() {
	mnkey=$(cat /etc/veles/veles.conf | grep masternodeprivkey | tail -n 1 | sed 's/masternodeprivkey=//g')
	if check_mn_key "${mnkey}"; then
		echo $mnkey
		return 0
	fi
	mnkey=$(cat /home/veles/.veles/veles.conf | grep masternodeprivkey | tail -n 1 | sed 's/masternodeprivkey=//g')

	if check_mn_key "${mnkey}"; then
		echo $mnkey
		return 0
	fi
	mnkey=$(cat /var/lib/veles/wallet.backup/veles.conf | grep masternodeprivkey | tail -n 1 | sed 's/masternodeprivkey=//g')

	if check_mn_key "${mnkey}"; then
		echo $mnkey
		return 0
	fi
	mnkey=$(cat /var/lib/veles/wallet/veles.conf | grep masternodeprivkey | tail -n 1 | sed 's/masternodeprivkey=//g')

	if check_mn_key "${mnkey}"; then
		echo $mnkey
		return 0
	fi

	return 1
}

find_public_ip() {
	ip=$(dig @resolver1.opendns.com ANY myip.opendns.com +short)

	if valid_ip "${ip}"; then
		echo "${ip}" | head -n 1
		return 0
	fi

	return 1
}

get_random_ascii() {
	head -c30 /dev/urandom | base64 | cut -c 1-$1
}

get_random_alnum() {
	head -c30 /dev/urandom | base64 | tr -cd '[:alnum:]._-' | cut -c 1-$1
}

pre_config_wizard() {
	vars_file=$1

	# Install dependencies of wizard itself (dialog)
	install_dialog_deps

	# Reinstall
	if [ -f /usr/bin/velesctl ]; then
		reinstall_msg="Choose [Next] to reinstall existing Veles Core Masternode on this system. The process will also: reset all Veles Core configuration"

		if ps aux | grep "/velesd" | grep -v grep > /dev/null; then
			reinstall_msg="${reinstall_msg}, stop all running velesd instances"
		fi

		if [ -f "${WALLET_DIR}/wallet.dat" ]; then
			reinstall_msg="${reinstall_msg}, move your previous wallet to backup location"
		fi

		dialog --backtitle "${BACKTITLE}" --title "${TITLE} [Warning]" --yesno "${reinstall_msg}" 10 60 || return 1
		killall velesd

		# Wallet backup
		if [ -f "${WALLET_DIR}/wallet.dat" ]; then
			#dialog --yes-label "Next" --no-label "Exit" --backtitle "${BACKTITLE}" --title "${TITLE}" --yesno "Your current wallet will be backed up and moved to: ${BACKUP_DIR}. Choose [Next] to continue." 8 60 || return 1
			if [ -d "${BACKUP_DIR}" ]; then
				mv "${BACKUP_DIR}" "${BACKUP_DIR}.2"
			fi
			cp -a "${WALLET_DIR}" "${BACKUP_DIR}"
		fi
	else
		# Welcome / exit
		dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --yes-label "Next" --no-label "Exit" --yesno 'Choose [Next] to install Veles Core Masternode on this system. It will require public IP address with access to public ports 443,21337 as well as local privileged port 53' 8 60 || return 1
	fi

	# Server ip dialog
	dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Looking up external IP address ...' 8 55
	server_ip=$(find_public_ip)

	if valid_ip "${server_ip}"; then
		dialog --backtitle "$BACKTITLE" --title "$TITLE" --yes-label "Next" --no-label "Change" --yesno "External IP address detected: ${server_ip}, choose Next to use it for the current installation" 8 55 || server_ip=""
	fi

	if ! valid_ip "${server_ip}"; then
		server_ip=$(dialog --stdout --backtitle "${BACKTITLE}" --inputbox "Enter your server's public IP address:" 8 50)
	fi

	while ! valid_ip "${server_ip}"; do
		dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --msgbox 'You need to enter a valid public IP address' 8 40
		server_ip=$(dialog --stdout --backtitle "${BACKTITLE}" --inputbox "Enter your server's public IP address:" 8 50)

		if [[ $server_ip == '' ]]; then
			dialog --backtitle "$BACKTITLE" --title "$TITLE" --yesno "Do you wish to exit and cancel the installation?" 8 50 && return 1
		fi
	done

	# Masternode key dialog
	mnkey=$(find_mn_key)

	if [[ "$mnkey" != '' ]]; then
		dialog --backtitle "$BACKTITLE" --title "$TITLE" --yesno "Previous Veles Masternode Private Key has been found: ${mnkey}  Do you wish to use it for current installation?" 10 57 || mnkey=""
	fi

	if [[ "$mnkey" == '' ]]; then
		mnkey=$(dialog --stdout --backtitle "$BACKTITLE" --inputbox "Enter your Masternode Private Key, or leave this blank to generete new one after the wallet installation." 8 60)
	fi

	while ! check_mn_key $mnkey; do
		if [[ "${mnkey}" == "" ]]; then
			mnkey="MASTERNODE_KEY_UNSET"
			break
		fi
		mnkey=$(dialog --stdout --backtitle "$BACKTITLE" --inputbox "Incorrect Masternode Key Format. Enter valid Masternode Private Key, or leave this blank to generete new one after the wallet installation." 10 60)
		length=${#mnkey}
	done

	echo "# Autogenerated by Veles Core Masternode installation program" > $vars_file
	echo -e "server_ip\t\t${server_ip}" >> $vars_file
	echo -e "velesd:rpcuser\t\t"$(get_random_alnum $((12 + RANDOM % 5))) >> $vars_file
	echo -e "velesd:rpcpassword\t"$(get_random_alnum $((40 + RANDOM % 10))) >> $vars_file
	echo -e "velesd:mnkey\t\t${mnkey}" >> $vars_file
	echo -e "velesctl:rpcuser\t"$(get_random_alnum $((12 + RANDOM % 5))) >> $vars_file
	echo -e "velesctl:rpcpassword\t"$(get_random_alnum $((40 + RANDOM % 10))) >> $vars_file

	# Just show the info
	echo -e "\n\n### Following configuration have been generated for the installation:"
	cat $vars_file | grep -v "#"
	echo -e "### (Masternode key will be set in later stage)\n"

	return 0
}

post_config_wizard() {
	if [ -f "${BACKUP_DIR}/wallet.dat" ]; then
		choice="YES"
		dialog --backtitle "$BACKTITLE" --title "$TITLE" --yes-label "Next" --no-label "Skip" --yesno "Press Next to import wallet from previous installation. If skipped it will be found in: ${BACKUP_DIR}/wallet.dat" 10 55 && choice="YES" || choice="NO"

		if [[ $choice == "YES" ]]; then
			dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Stopping Veles Core daemon ...' 3 40
			velesctl stop system.wallet.velesCoreDaemon > /dev/null
			cp -a "${BACKUP_DIR}/wallet.dat" "${WALLET_DIR}/"
			dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Starting Veles Core daemon ...' 3 40
			velesctl start system.wallet.velesCoreDaemon > /dev/null
		fi
	fi

	return 0
}

first_run_wizard() {
		while velesctl status system.wallet.velesCoreDaemon | grep STARTING > /dev/null; do
			dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Veles Core daemon is starting, please wait ...' 8 50
			sleep 10
		done

		if velesctl status system.wallet.velesCoreDaemon | grep RUNNING > /dev/null; then
			if grep MASTERNODE_KEY_UNSET /etc/veles/veles.conf > /dev/null; then
				mnkey=$(veles-cli masternode genkey)

				while ! check_mn_key ${mnkey}; do
					dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Veles Core wallet is getting ready, please wait ...' 8 50
					sleep 10
					mnkey=$(veles-cli masternode genkey)
				done

				if check_mn_key ${mnkey}; then
					dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --msgbox 'Your new Masternode Private Key is: ${mnkey}' 8 56
					echo -e "\n\n### Your new Masternode Private Key is: ${mnkey} ###\n"
					dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Stopping Veles Core daemon ...' 3 40
					velesctl stop system.wallet.velesCoreDaemon > /dev/null
					dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Patching /etc/veles/veles.conf ...' 3 40
					sed -i "s/#masternodeprivkey=/masternodeprivkey=/g" /etc/veles/veles.conf
					sed -i 's/MASTERNODE_KEY_UNSET/${mnkey}/g' /etc/veles/veles.conf
					sed -i 's/masternode=0/masternode=1/g' /etc/veles/veles.conf
					dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Starting Veles Core daemon ...' 3 40
					velesctl start system.wallet.velesCoreDaemon > /dev/null
				else
					dialog --backtitle "${BACKTITLE}" --title "${TITLE}: Error" --msgbox 'Failed to generate Masternode Private Key, please check in /var/log/veles/' 8 56
				fi
			fi
		else
			dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --infobox 'Veles Core daemon is not running, please check in /var/log/veles/' 8 50
			return 1
		fi

	dialog --backtitle "${BACKTITLE}" --title "${TITLE}" --ok-label "Finish" --msgbox 'Veles Core Masternode 2nd gen. has been succesfully installed! Check your node status anytime by typing: "veles-cli masternode status" and the state of all sub-services using "velesctl status": ' 10 55
	return 0
}

