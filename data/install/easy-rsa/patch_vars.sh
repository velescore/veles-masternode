# Patches EasyRSA config with custom vars
RSA_VARS_FILE="/usr/share/veles/easy-rsa/vars"
CF_VARS_FILE="./install/easy-rsa/vars.cf"

patch_easyrsa2_vars() {
	rsa_vars=$1
	cf_vars=$2

        while read line; do
		if [[ $line == '' || $(echo $line | cut -c1-1) == '#' ]]; then
			continue
		fi

                name=$(echo $line | awk '{print $1}') 2> /dev/null
                value=$(echo $line | sed "s/${name}//g" | sed 's/^[ \t]//g') 2> /dev/null

		if [[ $name == '' ]] || [[ $value == '' ]]; then
			continue
		fi

		# Patch RSA file entry, all know versions
		# Global options
		sed -i "s/^[# ]*export ${name}.*\$/export ${name}=${value}	# Veles Core/g" "$rsa_vars"			# 2.x
		sed -i "s/^[# ]*set_var EASYRSA_${name}.*\$/set_var EASYRSA_${name} ${value}	# Veles Core/g" "$rsa_vars"	# Veles Core default/g'	# 3.x
		# Certificate options
		sed -i "s/^[# ]*export KEY_${name}.*\$/export KEY_${name}=${value}	# Veles Core/g" "$rsa_vars"			# Veles Core default/g'			# 2.x
		sed -i "s/^[# ]*set_var EASYRSA_REQ_${name}.*\$/set_var EASYRSA_REQ_${name} ${value}	# Veles Core/g"	"$rsa_vars"	# Veles Core default/g'	# 3.x
        done < $cf_vars
}

patch_easyrsa2_vars $RSA_VARS_FILE $CF_VARS_FILE

