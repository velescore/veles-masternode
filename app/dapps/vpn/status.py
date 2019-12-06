#!/usr/bin/env python

class VPNStatusService(object):
	def __init__(self, config, logger, vpn_gateway):
		self.config = config
		self.logger = logger
		self.vpn_gateway = vpn_gateway

	def service_status(self):
		return {**self.vpn_gateway.get_status(), 'network_usage': self.get_usage()}

	def get_usage():
		bytes_in, bytes_out = self._get_network_bytes(self.config['dapps.vpn'].get('tun_interface', 'tun1'))
		return { 'bytes_in': bytes_in, 'bytes_out': bytes_out}

	def _get_network_bytes(interface):
		for line in open('/proc/net/dev', 'r'):
			if interface in line:
				data = line.split('%s:' % interface)[1].split()
				rx_bytes, tx_bytes = (data[0], data[8])
				return (int(rx_bytes), int(tx_bytes))