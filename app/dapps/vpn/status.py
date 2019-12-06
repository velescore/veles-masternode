#!/usr/bin/env python

class VPNStatusService(object):
	def __init__(self, config, logger, vpn_gateway, stats_repo):
		self.config = config
		self.logger = logger
		self.vpn_gateway = vpn_gateway
		self.stats_repo = stats_repo

	def service_status(self):
		state_name = 'ACTIVE'

		try:
			server_stats = self.vpn_gateway.get_status()
		except Exception as e:
			server_stats = {}
			state_name = 'INACTIVE'
			self.logger.error('VPNStatusService::service_status: Failed to obtain OpenVPN server status')

		try:
			usage_stats = self.get_usage()
		except Exception as e:
			usage_stats = {}
			usage_stats = 'INACTIVE'
			self.logger.error('VPNStatusService::service_status: Failed to obtain OpenVPN network device status')

		return {**server_stats, 'usage_stats': usage_stats, 'state_name': state_name}

	def get_usage(self):
		bytes_in, bytes_out = self._get_network_bytes(self.config['dapps.vpn'].get('tun_interface', 'tun1'))
		return { 'bytes_in': bytes_in, 'bytes_out': bytes_out}

	def _get_network_bytes(self, interface):
		for line in open('/proc/net/dev', 'r'):
			if interface in line:
				data = line.split('%s:' % interface)[1].split()
				rx_bytes, tx_bytes = (data[0], data[8])
				return (int(rx_bytes), int(tx_bytes))