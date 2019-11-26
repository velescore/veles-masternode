import os, subprocess, re
import unicodedata
from hashlib import blake2b
from random import random

class VelesCertificateService(object):
	def __init__(self, script_path = '/usr/share/veles/easy-rsa', tpl_path = '/etc/veles/vpn/'):
		self.script_path = script_path
		self.tpl_path = tpl_path

	def get_new_certificate(self, cn=None):
		if not cn:
			h = blake2b(digest_size=15)
			h.update(str(random()).encode('utf-8'))
			cn = h.hexdigest()
		cn = self.normalize(cn)

		try:
			subprocess.run(os.path.join(self.script_path, 'build-key-auto %s' % cn), shell=True, check=True)

			with open(os.path.join(self.script_path, 'keys/%s.crt' % cn), 'r') as crtfile:
				crtval = crtfile.read()
			with open(os.path.join(self.script_path, 'keys/%s.key' % cn), 'r') as keyfile:
				keyval = keyfile.read()
			with open(os.path.join(self.script_path, 'keys/ca.crt'), 'r') as cafile:
				cafileval = cafile.read()

			result = {'cn': cn, 'certificate': crtval, 'key': keyval, 'ca': cafileval}
		except:
			result = False

		return result

	def make_openvpn_config(self, cert):
		with open(os.path.join(self.tpl_path, 'openvpn.client.conf'), 'r') as tpl_file:
			tpl = tpl_file.read()
		return str(tpl) + "\n<ca>\n" + cert['ca'] + "</ca>\n" \
			+ "<cert>\n" + cert['certificate'] + "</cert>\n" \
			+ "<key>\n" + cert['key'] + "</key>\n"

	def make_openvpn_shielded_config(self, cert):
		with open(os.path.join(self.tpl_path, 'openvpn-shield.client.conf'), 'r') as tpl_file:
			tpl = tpl_file.read()
		return str(tpl) + "\n<ca>\n" + cert['ca'] + "</ca>\n" \
			+ "<cert>\n" + cert['certificate'] + "</cert>\n" \
			+ "<key>\n" + cert['key'] + "</key>\n"

	def make_stunnel_config(self, cert):
		with open(os.path.join(self.tpl_path, 'stunnel.client.conf'), 'r') as tpl_file:
			tpl = tpl_file.read()
		return str(tpl)

	def normalize(self, value):
		value = re.sub('[^\w\s-]', '', value).strip().lower()
		value = re.sub('[-\s]+', '-', value)
		return value
