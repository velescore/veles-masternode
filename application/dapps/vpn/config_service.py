import os
#import unicodedata

class ConfigProvisioningService(object):
	""" Provides configuration files for various dVPN clients """
	def __init__(self, config, logger):
		self.tpl_path = config['dapps.vpn'].get('tpl_path', '/etc/veles/vpn')
		self.logger = logger

	def make_openvpn_config(self, cert):
		with open(os.path.join(self.tpl_path, 'openvpn.client.conf'), 'r') as tpl_file:
			tpl = tpl_file.read()
		return str(tpl) + "\n<ca>\n" + cert.ca_certificate + "</ca>\n" \
			+ "<cert>\n" + cert.certificate + "</cert>\n" \
			+ "<key>\n" + cert.private_key + "</key>\n"

	def make_openvpn_shielded_config(self, cert):
		with open(os.path.join(self.tpl_path, 'openvpn-shield.client.conf'), 'r') as tpl_file:
			tpl = tpl_file.read()
		return str(tpl) + "\n<ca>\n" + cert.ca_certificate + "</ca>\n" \
			+ "<cert>\n" + cert.certificate + "</cert>\n" \
			+ "<key>\n" + cert.private_key + "</key>\n"

	def make_stunnel_config(self, cert):
		with open(os.path.join(self.tpl_path, 'stunnel.client.conf'), 'r') as tpl_file:
			tpl = tpl_file.read()
		return str(tpl)
