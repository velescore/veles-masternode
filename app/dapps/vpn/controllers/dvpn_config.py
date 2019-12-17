#!/usr/bin/env python
import asyncio, sys, json, version
from controllers.interfaces import AbstractSigningController

class ConfigProvisioningController(AbstractSigningController):
	methods = ['getOpenVPNShieldedConfig', 'getStunnelConfig', 'getStunnelCertificate', 
		'getCACertificate', 'getAllConfigData']

	def __init__(self, config, logger, signing_service, certificate_service, config_service):
		super().__init__(config, logger, signing_service)
		self.certificate_service = certificate_service
		self.config_service = config_service

	def set_routes(self, router):
		for method in self.methods:
			router.add_get('/api/%s' % method, self.handle)			# deprecated
			router.add_get('/api/dvpn/%s' % method, self.handle)

	@asyncio.coroutine
	def handle(self, request):
		method = request.path.split('/')[-1:]
		result = None
		text = None
		headers = {}
		cert = self.certificate_service.issue_new_certificate()

		if method == 'getCertificate':
			result = {
				'certificate_data': cert
			}
			headers = self.headers_json
		elif method == 'getOpenVPNConfig':
			text = str(self.config_service.make_openvpn_config(cert))
			headers = {
				"Content-Type": "application/x-openvpn-profile",
				"Content-Disposition": "attachment; filename=veles.ovpn"
				}
		elif method == 'getOpenVPNShieldedConfig':
			text = str(self.config_service.make_openvpn_shielded_config(cert))
			headers = {
				"Content-Type": "application/openvpn",
				"Content-Disposition": "attachment; filename=veles-shield.ovpn"
				}
		elif method == 'getStunnelConfig':
			text = str(self.config_service.make_stunnel_config(cert))
			headers = {
				"Content-Type": "application/stunnel",
				"Content-Disposition": "attachment; filename=veles.stunnel.conf"
				}
		elif method == 'getStunnelCertificate':
			text = str(cert.ca_certificate) + "\n" + str(cert.certificate) + "\n" + str(cert.private_key)
			headers = {
				"Content-Type": "application/openssl",
				"Content-Disposition": "attachment; filename=stunnel.pem"
				}
		elif method == 'getCACertificate':	# todo: finish - don't generate all the shit just fetch ca file
			text = str(cert.ca_certificate)
			headers = {
				"Content-Type": "application/openssl",
				"Content-Disposition": "attachment; filename=veles-ca.crt"
				}
		elif method == 'getAllConfigData':
			result = {
				'certificate_data': cert,
				'openvpn_config': self.config_service.make_openvpn_config(cert),
				'stunnel_config': self.config_service.make_stunnel_config(cert)
			}

		if text:
			return self.response(text, headers=headers)
		else:
			return self.json_response(result, extra_headers=headers)
