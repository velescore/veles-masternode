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
MN_VERSION="1.99.05"
CORE_VERSION="0.18.1.3"
BACKTITLE="Veles Core Masternode Installation"	# ${MN_VERSION}/${CORE_VERSION}"
TITLE="Veles Core Masternode"
WALLET_DIR="/var/lib/veles/wallet"
BACKUP_DIR="/root/veles-wallet-backup"

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

mn_dialog() {
	dialog --backtitle "${BACKTITLE}" --title "${TITLE}" "$@"
}

wiz_progress() {
	mn_dialog --progressbox 15 65
}

wiz_progress_wait() {
	mn_dialog --programbox 15 65
}

wiz_info() {
	mn_dialog --infobox "${1}" 8 45
}

wiz_info_tiny() {
	mn_dialog --infobox "${1}" 3 40
}

wiz_message() {
	mn_dialog --msgbox "${1}" 10 57
}

install_dialog_deps() {
	echo -e "\n* Preparing the installator ..."
	echo "  * Updating system package list..."
	apt-get update
	if ! dpkg --get-selections | grep "gawk" > /dev/null; then
		echo "  * Installing dependencies: gawk ..."
		apt-get install --no-install-recommends -y gawk
	fi
	if ! dpkg --get-selections | grep "sed" > /dev/null; then
		echo "  * Installing dependencies: sed ..."
		apt-get install --no-install-recommends -y sed
	fi
	if ! dpkg --get-selections | grep "psmisc" > /dev/null; then
		echo "  * Installing dependencies: psmisc ..."
		apt-get install --no-install-recommends -y psmisc
	fi
	if ! dpkg --get-selections | grep "dialog" > /dev/null; then
		echo "  * Installing dependencies: dialog ..."
		apt-get install --no-install-recommends -y dialog
	fi
	if ! dpkg --get-selections | grep "dnsutils" > /dev/null; then
		echo "  * Installing dependencies: dnsutils ..."
		apt-get install --no-install-recommends -y dnsutils
	fi
}

#fetch_mn_state() {
#	veles-cli -conf=/etc/veles/veles.conf masternode status | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])"
#}

check_mn_key() {
	mnkey="${1}"
	length=${#mnkey}

	[ $length -gt 48 ] && [ $length -lt 65 ] && return 0 || return 1     # TODO: better mn key validity checks
}

check_signing_key() {
	sigkey="${1}"
	length=${#sigkey}

	[ $length -gt 32 ] && [ $length -lt 36 ] && return 0 || return 1     # TODO: better sig key validity checks
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
	mnkey=$(cat ${BACKUP_DIR}/veles.conf | grep masternodeprivkey | tail -n 1 | sed 's/masternodeprivkey=//g')

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

find_signing_key() {
	sigkey=$(cat /etc/veles/mn.conf | grep -v '{{mn' | grep signing_key | tail -n 1 | sed 's/signing_key=//g')
	if check_signing_key "${sigkey}"; then
		echo $sigkey
		return 0
	fi

	return 1
}

find_public_ip() {
	ip=$( dig @resolver1.opendns.com ANY myip.opendns.com +short )

	if valid_ip "${ip}"; then
		echo "${ip}" | head -n 1
		return 0
	fi

	ip=$( host myip.opendns.com resolver1.opendns.com | grep "myip.opendns.com has" | awk '{print $4}' )

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
	opts_file=$2

	# Install dependencies of wizard itself (dialog)
	install_dialog_deps

	# Reinstall
	if [ -f /usr/bin/velesctl ]; then
		reinstall_msg="Choose <Next> to reinstall existing Veles Core Masternode on this system. The process will also: reset Veles Core configuration"

		if ps aux | grep "/velesd" | grep -v grep > /dev/null; then
			reinstall_msg="${reinstall_msg}, and stop all running velesd instances."
		fi

		#if [ -f "${WALLET_DIR}/wallet.dat" ]; then
		#	reinstall_msg="${reinstall_msg}, move your previous wallet to backup location"
		#fi

		dialog --backtitle "${BACKTITLE}" --title "${TITLE} [Warning]" --yesno "${reinstall_msg}" 10 60 || return 1

		# Stop all or running services
		mn_dialog --infobox 'Stopping Veles Core Masternode services...' 3 45
		velesctl stop all > /dev/null
		systemctl stop veles-mn  > /dev/null
		# Just to be reallly sure
		killall velesd 2> /dev/null
		killall openvpn 2> /dev/null
		killall redis-server 2> /dev/null
		killall stunnel4 2> /dev/null
	else
		# Welcome / exit
		mn_dialog --yes-label "Next" --no-label "Exit" --yesno 'Choose <Next> to install Veles Core Masternode 2nd gen. on this system. It will require public IP address with access to public ports 53,443 and 21337' 8 60 || return 1
	fi


	# Wallet backup
	WALLET_IS_IMPORTED=0
	if [ -f "${WALLET_DIR}/wallet.dat" ]; then
		timestamp=$(date +%s)
		mkdir "${BACKUP_DIR}" 2> /dev/null
		cp -au "${WALLET_DIR}" "${BACKUP_DIR}"/data
		cp -a "${WALLET_DIR}/wallet.dat" "${BACKUP_DIR}/wallet.dat.${timestamp}"
		cp -a "${WALLET_DIR}/wallet.dat" "${BACKUP_DIR}/wallet.dat"

		choice="Next"
		dialog --yes-label "Next" --no-label "Keep old" --backtitle "${BACKTITLE}" --title "${TITLE}" --yesno "Choose <Next> to import your current wallet and create clean datadir (recommended) or <Keep old> to use your current datadir from previous installation. Your current wallet file has been backed up to: ${BACKUP_DIR}." 11 60 || choice="Keep"

		if [[ "${choice}" == "Next" ]] && [ -f "${BACKUP_DIR}/wallet.dat" ]; then
			mn_dialog --infobox 'Cleaning datadir and importing wallet ...' 3 50
			rm -r "${WALLET_DIR}/*"
			cp -a "${BACKUP_DIR}/wallet.dat" "${WALLET_DIR}"
			WALLET_IS_IMPORTED=1
		fi
	fi

	# Upgrade from 1st gen
	if [ -f /etc/systemd/system/veles.service ]; then
		mn_dialog --infobox 'Stopping previous Veles Core daemon ...' 3 40
		systemctl stop veles
		killall velesd >/dev/null
		mn_dialog --infobox 'Disabling previous Veles Core service ...' 3 40
		systemctl disable veles
	fi

	# Server ip dialog
	mn_dialog --infobox 'Looking up external IP address ...' 8 55
	server_ip=$(find_public_ip)

	if valid_ip "${server_ip}"; then
		mn_dialog --yes-label "Next" --no-label "Change" --yesno "External IP address detected: ${server_ip}, choose <Next> to use it for the current installation" 8 55 || server_ip=""
	fi

	if ! valid_ip "${server_ip}"; then
		server_ip=$(dialog --stdout --backtitle "${BACKTITLE}" --inputbox "Enter your server's public IP address:" 8 50)
	fi

	while ! valid_ip "${server_ip}"; do
		mn_dialog --msgbox 'You need to enter a valid public IP address' 8 40
		server_ip=$(dialog --stdout --backtitle "${BACKTITLE}" --inputbox "Enter your server's public IP address:" 8 50)

		if [[ $server_ip == '' ]]; then
			mn_dialog --yesno "Do you wish to exit and cancel the installation?" 8 50 && return 1
		fi
	done

	# Masternode key dialog
	mnkey=$(find_mn_key)

	if [[ "$mnkey" != '' ]]; then
		mn_dialog --yesno "Previous Veles Masternode Private Key has been found: ${mnkey}  Do you wish to use it for current installation?" 10 57 || mnkey=""
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

	# Signing address dialog
	sigkey=$(find_signing_key)

	if [[ "$sigkey" != '' ]] && [ WALLET_IS_IMPORTED == 1]; then
		if check_signing_key $sigkey; then
			mn_dialog -yes-label "Next" --yesno "Previous Veles Masternode Signing Key has been found: ${sigkey}  Choose <Next> to use it for current installation? (recommended)" 10 57 || sigkey=""
		else
			sigkey=''
		fi
	fi

	if [[ "$sigkey" == '' ]]; then
		sigkey="SIGNING_KEY_UNSET"
	fi

	# Optional services
	INPUT=/tmp/menu.sh.$$		# Temp file to store user selection from dialog

	# trap and delete temp files
	trap "rm $INPUT; exit" SIGHUP SIGINT SIGTERM
	
	dialog --checklist "Use [space] to select optional masternode services:" 10 55 5 \
        1 "Shadowsocks" on 2>"${INPUT}"

  menuitem=$(<"${INPUT}")
  optionals=""

	# Write out optional service list
	echo "# Settings generated by Veles Core Masternode Installator" > $opts_file
	echo "# on host "$(hostname)" at "$(date) >> $opts_file
	echo "# This file contains optional masternode services or dApps" >> $opts_file
	echo "# that will be installed on the masternode." >> $opts_file

  # convert coices to real names
	case $menuitem in
		1) echo "shadowsocks" >> $opts_file;;
	esac

	# Write out settings
	echo "# Settings generated by Veles Core Masternode Installator" > $vars_file
	echo "# on host "$(hostname)" at "$(date) >> $vars_file
	echo -e "server_ip\t\t${server_ip}" >> $vars_file
	echo -e "velesd:rpcuser\t\t"$(get_random_alnum $((12 + RANDOM % 5))) >> $vars_file
	echo -e "velesd:rpcpassword\t"$(get_random_alnum $((40 + RANDOM % 10))) >> $vars_file
	echo -e "velesd:mnkey\t\t${mnkey}" >> $vars_file
	echo -e "velesctl:rpcuser\t"$(get_random_alnum $((12 + RANDOM % 5))) >> $vars_file
	echo -e "velesctl:rpcpassword\t"$(get_random_alnum $((40 + RANDOM % 10))) >> $vars_file
	echo -e "mn:signing_key\t\t${sigkey}" >> $vars_file

	# Just show the info
	cat $vars_file | wiz_progress_wait

	return 0
}

pre_config_auto() {
	vars_file=$1
	opts_file=$2

	# Install dependencies of wizard itself (dialog)
	install_dialog_deps

	# Reinstall
	if [ -f /usr/bin/velesctl ]; then
		if ps aux | grep "/velesd" | grep -v grep > /dev/null; then
			reinstall_msg="${reinstall_msg}, and stop all running velesd instances."
		fi

		# Stop all or running services
		echo 'Stopping current Veles Core Masternode services...'
		velesctl stop all
		systemctl stop veles-mn #| wiz_progress
		# Just to be reallly sure
		killall velesd 2> /dev/null
		killall openvpn 2> /dev/null
		killall redis-server 2> /dev/null
		killall stunnel4 2> /dev/null
	fi

	# Wallet backup
	WALLET_IS_IMPORTED=0
	if [ -f "${WALLET_DIR}/wallet.dat" ]; then
		timestamp=$(date +%s)
		mkdir "${BACKUP_DIR}" 2> /dev/null
		cp -au "${WALLET_DIR}" "${BACKUP_DIR}"/data
		cp -a "${WALLET_DIR}/wallet.dat" "${BACKUP_DIR}/wallet.dat.${timestamp}"
		cp -a "${WALLET_DIR}/wallet.dat" "${BACKUP_DIR}/wallet.dat"

		choice="Next"
		echo "[auto] Chose <Next> to import the current wallet and create clean datadir (recommended) NOT <Keep old> to use the current datadir from previous installation. Your current wallet file has been backed up to: ${BACKUP_DIR}."

		if [[ "${choice}" == "Next" ]] && [ -f "${BACKUP_DIR}/wallet.dat" ]; then
			mn_dialog --infobox 'Cleaning datadir and importing wallet ...' 3 50
			rm -r "${WALLET_DIR}/*"
			cp -a "${BACKUP_DIR}/wallet.dat" "${WALLET_DIR}"
			WALLET_IS_IMPORTED=1
		fi
	fi

	# Upgrade from 1st gen
	if [ -f /etc/systemd/system/veles.service ]; then
		systemctl stop veles
		killall velesd >/dev/null
		systemctl disable veles
	fi

	# Server ip dialog
	server_ip=$(find_public_ip)

	if ! valid_ip "${server_ip}"; then
		echo "[error] Could not automatically determine external IP address but cannot ask for it when running in a non-interactive mode"
		exit 1
	fi

	# Masternode key dialog
	mnkey=$(find_mn_key)

	if check_mn_key $mnkey; then
		echo "[auto] MASTERNODE_KEY found: ${mnkey}"
	else
		echo "[auto] MASTERNODE_KEY not found, will generate new one ..."
		mnkey="MASTERNODE_KEY_UNSET"
	fi

	# Signing address dialog
	sigkey=$(find_signing_key)

	if check_signing_key $sigkey; then
		echo "[auto] SIGNING_KEY found: ${sigkey}"
	else
		echo "[auto] SIGNING_KEY not found, will generate new one ..."
		sigkey="SIGNING_KEY_UNSET"
	fi

	# Write out default optional service list
	echo "# Settings generated by Veles Core Masternode Installator" > $opts_file
	echo "# on host "$(hostname)" at "$(date) >> $opts_file
	echo "# This file contains optional masternode services or dApps" >> $opts_file
	echo "# that will be installed on the masternode." >> $opts_file
	echo "shadowsocks" >> $opts_file

	# Write out the settings
	echo "# Settings generated by Veles Core Masternode Installator:" > $vars_file
	echo -e "server_ip\t\t${server_ip}" >> $vars_file
	echo -e "velesd:rpcuser\t\t"$(get_random_alnum $((12 + RANDOM % 5))) >> $vars_file
	echo -e "velesd:rpcpassword\t"$(get_random_alnum $((40 + RANDOM % 10))) >> $vars_file
	echo -e "velesd:mnkey\t\t${mnkey}" >> $vars_file
	echo -e "velesctl:rpcuser\t"$(get_random_alnum $((12 + RANDOM % 5))) >> $vars_file
	echo -e "velesctl:rpcpassword\t"$(get_random_alnum $((40 + RANDOM % 10))) >> $vars_file
	echo -e "mn:signing_key\t\t${sigkey}" >> $vars_file

	# Just show the info
	cat $vars_file

	return 0
}

post_config_wizard() {
	if [ -f "/home/veles/.veles/wallet.dat" ] && [ ! "${WALLET_DIR}/wallet.dat" ]; then
		choice="YES"
		mn_dialog --yes-label "Next" --no-label "Skip" --yesno "Press Next to import wallet from previous generation of Veles Core Masternode." 10 55 && choice="YES" || choice="NO"

		if [[ $choice == "YES" ]]; then
			mn_dialog --infobox 'Restarting Veles Core: Stopping daemon...' 4 45
			velesctl stop system.wallet.velesCoreDaemon > /dev/null
			cp -a "/home/veles/.veles/wallet.dat" "${WALLET_DIR}/"
			mn_dialog --infobox 'Restarting Veles Core: Sarting daemon... (this might take a while)' 4 45
			velesctl start system.wallet.velesCoreDaemon > /dev/null
		fi
	fi

	return 0
}

post_config_auto() {
	if [ -f "/home/veles/.veles/wallet.dat" ] && [ ! "${WALLET_DIR}/wallet.dat" ]; then
		choice="YES"
		echo "[auto] Pressing Next to import wallet from previous generation of Veles Core Masternode."

		if [[ $choice == "YES" ]]; then
			echo '[auto] Restarting Veles Core: Stopping daemon...'
			velesctl stop system.wallet.velesCoreDaemon > /dev/null
			cp -a "/home/veles/.veles/wallet.dat" "${WALLET_DIR}/"
			echo '[auto] Restarting Veles Core: Sarting daemon... (this might take a while)'
			velesctl start system.wallet.velesCoreDaemon > /dev/null
		fi
	fi

	return 0
}

first_run_wizard() {
		mn_dialog --infobox 'Starting Veles Masternode services ...' 4 35
		mn_dialog --tailbox /var/lib/veles/wallet/debug.log 20 165 || mn_dialog --infobox 'Loading Veles Core daemon ... ' 4 45 &

		while velesctl status system.wallet.velesCoreDaemon | grep STARTING > /dev/null; do
			sleep 5
		done
		killall dialog

		if velesctl status system.wallet.velesCoreDaemon | grep RUNNING > /dev/null; then

			if grep MASTERNODE_KEY_UNSET /etc/veles/veles.conf > /dev/null; then
				mnkey=$(veles-cli -conf=/etc/veles/veles.conf masternode genkey)
				mn_dialog --infobox 'Loading Veles Core wallet... ' 4 45

				while ! check_mn_key ${mnkey}; do
					mn_dialog --tailbox /var/lib/veles/wallet/debug.log 20 165 &
					sleep 10
					mnkey=$(veles-cli -conf=/etc/veles/veles.conf masternode genkey)
				done
				killall dialog

				if check_mn_key ${mnkey}; then
					mn_dialog --msgbox "Your new Masternode Private Key is: ${mnkey}" 8 56
					echo -e "\n\n### Your new Masternode Private Key is: ${mnkey} ###\n"
					mn_dialog --infobox 'Restarting Veles Core: Stopping daemon ... ' 4 45
					velesctl stop system.wallet.velesCoreDaemon > /dev/null
					mn_dialog --infobox 'Patching /etc/veles/veles.conf ...' 3 40
					sed -i "s/[# ]masternodeprivkey=MASTERNODE_KEY_UNSET/masternodeprivkey=${mnkey}/g" /etc/veles/veles.conf
					sed -i 's/[# ]masternode=0/masternode=1/g' /etc/veles/veles.conf
					mn_dialog --infobox 'Restarting Veles Core: Starting daemon ... (this might take a while)' 4 45
					velesctl start system.wallet.velesCoreDaemon > /dev/null
				else
					if [ -f /var/lib/veles/wallet/debug.log ]; then
						dialog --backtitle "${BACKTITLE}" --title "${TITLE}: Error" --msgbox 'Failed to generate Masternode Private Key, please check wallet log' 8 56
						mn_dialog --tailbox /var/lib/veles/wallet/debug.log 10 100
					else
						dialog --backtitle "${BACKTITLE}" --title "${TITLE}: Error" --msgbox 'Failed to generate Masternode Private Key, please check in /var/log/veles/' 8 56
					fi
				fi
			fi

			if grep SIGNING_KEY_UNSET /etc/veles/mn.conf > /dev/null; then
				sigkey=$(veles-cli -conf=/etc/veles/veles.conf getnewaddress legacy)
				mn_dialog --infobox 'Loading Veles Core wallet... ' 4 45

				while ! check_signing_key ${sigkey}; do
					mn_dialog --tailbox /var/lib/veles/wallet/debug.log 20 165 &
					sleep 30
					sigkey=$(veles-cli -conf=/etc/veles/veles.conf getnewaddress legacy)
				done
				killall dialog

				if check_signing_key ${sigkey}; then
					sed -i "s/[# ]signing_key=SIGNING_KEY_UNSET/signing_key=${sigkey}/g" /etc/veles/mn.conf
				else
					if [ -f /var/lib/veles/wallet/debug.log ]; then
						dialog --backtitle "${BACKTITLE}" --title "${TITLE}: Error" --msgbox 'Failed to generate Masternode Signing Key, please check wallet log' 8 56
						mn_dialog --tailbox /var/lib/veles/wallet/debug.log 10 100
					else
						dialog --backtitle "${BACKTITLE}" --title "${TITLE}: Error" --msgbox 'Failed to generate Masternode Signing Key, please check in /var/log/veles/' 8 56
					fi
				fi
			fi

		else
			# Try one last time
			sleep 10
			mn_dialog --infobox 'Waiting for Veles Core daemon ...' 3 40

			if velesctl status system.wallet.velesCoreDaemon | grep RUNNING > /dev/null || velesctl status system.wallet.velesCoreDaemon | grep STARTING > /dev/null; then
				first_run_wizard
			else
				mn_dialog --infobox 'Veles Core daemon is not running, please check wallet logs' 8 50
				if [ -f /var/lib/veles/wallet/debug.log ]; then
					mn_dialog --tailbox /var/lib/veles/wallet/debug.log 10 100

				elif [ -f /var/log/veles/velesctl.log ]; then
					mn_dialog --tailbox /var/lib/veles/wallet/debug.log 10 100
				fi
				return 1
			fi
		fi

	if velesctl status | grep FATAL; then
		mn_dialog --ok-label "Show report" --msgbox 'Some of the services has failed to start, please check which ones on the following screen and see service logs in /var/log/veles/services.d for more information' 10 55
		velesctl status | mn_dialog --programbox 15 65
		exit 1
	else
		mn_dialog --ok-label "Finish" --msgbox 'Veles Core Masternode 2nd gen. has been succesfully installed! Check your node status anytime by typing: "veles-cli -conf=/etc/veles/veles.conf masternode status" and the state of all sub-services using "velesctl status": ' 10 55
		exit 0
	fi
}

first_run_auto() {
		echo '[auto] Starting Veles Masternode services ...'
	
		echo -n '[auto] Waiting for Veles Core wallet to start ...'
		while velesctl status system.wallet.velesCoreDaemon | grep STARTING > /dev/null; do
			sleep 5
			echo -n '.'
		done
		echo ' done'
	
		if velesctl status system.wallet.velesCoreDaemon | grep RUNNING > /dev/null; then

			if grep MASTERNODE_KEY_UNSET /etc/veles/veles.conf > /dev/null; then
				mnkey=$(veles-cli -conf=/etc/veles/veles.conf masternode genkey)
				echo '[auto] Loading Veles Core wallet... '

				echo -n '[auto] Waiting for Veles Core to generate MASTERNODE_KEY ...'
				while ! check_mn_key ${mnkey}; do
					sleep 10
					echo -n '.'
					mnkey=$(veles-cli -conf=/etc/veles/veles.conf masternode genkey)
				done
				echo ' done'

				if check_mn_key ${mnkey}; then
					echo -e "\n\n### Your new Masternode Private Key is: ${mnkey} ###\n"
					echo '[auto] Restarting Veles Core: Stopping daemon ... '
					velesctl stop system.wallet.velesCoreDaemon > /dev/null
					echo '[auto] Patching /etc/veles/veles.conf ...'
					sed -i "s/[# ]masternodeprivkey=MASTERNODE_KEY_UNSET/masternodeprivkey=${mnkey}/g" /etc/veles/veles.conf
					sed -i 's/[# ]masternode=0/masternode=1/g' /etc/veles/veles.conf
					echo '[auto] Restarting Veles Core: Starting daemon ... (this might take a while)'
					velesctl start system.wallet.velesCoreDaemon > /dev/null
				else
					if [ -f /var/lib/veles/wallet/debug.log ]; then
						echo '[error] Failed to generate Masternode Private Key, showing last 100 lines of debug log:'
						tail -n 100 /var/lib/veles/wallet/debug.log
					else
						echo '[error] Failed to generate Masternode Private Key, no debug log to show either!'
					fi
				fi
			fi

			if grep SIGNING_KEY_UNSET /etc/veles/mn.conf > /dev/null; then
				sigkey=$(veles-cli -conf=/etc/veles/veles.conf getnewaddress legacy)
				echo '[auto] Loading Veles Core wallet... '

				echo -n '[auto] Waiting for Veles Core to generate MASTERNODE_KEY ...'
				while ! check_signing_key ${sigkey}; do
					sleep 30
					echo -n '.'
					sigkey=$(veles-cli -conf=/etc/veles/veles.conf getnewaddress legacy)
				done
				echo ' done'

				if check_signing_key ${sigkey}; then
					echo -e "\n\n### New Signing Key is: ${sigkey} ###\n"
					sed -i "s/[# ]signing_key=SIGNING_KEY_UNSET/signing_key=${sigkey}/g" /etc/veles/mn.conf
				else
					if [ -f /var/lib/veles/wallet/debug.log ]; then
						echo '[error] Failed to generate Masternode Private Key, showing last 100 lines of debug log:'
						tail -n 100 /var/lib/veles/wallet/debug.log
					else
						echo '[error] Failed to generate Masternode Private Key, no debug log to show either!'
					fi
				fi
			fi

		else
			# Try one last time
			sleep 10
			echo '[auto] Waiting for Veles Core daemon ...'

			if velesctl status system.wallet.velesCoreDaemon | grep RUNNING > /dev/null || velesctl status system.wallet.velesCoreDaemon | grep STARTING > /dev/null; then
				first_run_auto
			else
				echo '[auto] Veles Core daemon is not running, please check wallet logs'
				if [ -f /var/lib/veles/wallet/debug.log ]; then
					tail -n 100 /var/lib/veles/wallet/debug.log

				elif [ -f /var/log/veles/velesctl.log ]; then
					tail -n 100 /var/log/veles/velesctl.log
				fi
				return 1
			fi
		fi

	if velesctl status | grep FATAL; then
		echo 'Some of the services has failed to start, please check which ones on the following screen and see service logs in /var/log/veles/services.d for more information'
		velesctl status
		echo -e '\n\nTrace logs:\n'
		cat /var/log/veles/services.d/*
		exit 1
	else
		echo 'Veles Core Masternode 2nd gen. has been succesfully installed! Check your node status anytime by typing: "veles-cli -conf=/etc/veles/veles.conf masternode status" and the state of all sub-services using "velesctl status": '
		export NON_INTERACTIVE_INSTALL_SUCCESS=1
		velesctl status
		veles-cli masternode status
		exit 0
	fi
}
