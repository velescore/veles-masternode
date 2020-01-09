import os, subprocess, re
from hashlib import blake2b
from random import random

class RSACertificate(object):
	""" Represents an RSA certificate with private key and CA certificate """
	def __init__(self, common_name, certificate, private_key, ca_certificate):
		self.common_name = common_name
		self.certificate = certificate
		self.private_key = private_key
		self.ca_certificate = ca_certificate

class CertificateProvisioningService(object):
	""" Issues RSA certificates to be used with Veles dVPN """
	def __init__(self, config, logger):
		self.script_path = config['dapps.vpn'].get('rsa_path', '/usr/share/veles/easy-rsa')
		self.logger = logger

	def issue_new_certificate(self, cn=None):
		if not cn:
			h = blake2b(digest_size=15)
			h.update(str(random()).encode('utf-8'))
			cn = h.hexdigest()

		cn = self.normalize_cn(cn)
		self.logger.info("CertificateProvisioningService: Issuing new dVPN certificate with CN {}".format(cn))

		try:
			subprocess.run(os.path.join(self.script_path, 'build-key-auto %s' % cn), shell=True, check=True)

			with open(os.path.join(self.script_path, 'keys/%s.crt' % cn), 'r') as crtfile:
				crtval = crtfile.read()
			with open(os.path.join(self.script_path, 'keys/%s.key' % cn), 'r') as keyfile:
				keyval = keyfile.read()
			with open(os.path.join(self.script_path, 'keys/ca.crt'), 'r') as cafile:
				cafileval = cafile.read()

			return RSACertificate(
				common_name = cn,
				certificate = crtval,
				private_key = keyval,
				ca_certificate = cafileval,
				)
		except:
			return False

		return result

	def normalize_cn(self, value):
		value = re.sub('[^\w\s-]', '', value).strip().lower()
		value = re.sub('[-\s]+', '-', value)
		return value
