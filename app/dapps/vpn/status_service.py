#!/usr/bin/env python
from dapps.interfaces import AbstractStatusService

class VPNStatusService(AbstractStatusService):
	def __init__(self, config, logger, vpn_gateway, metric_service):
		self.config = config
		self.logger = logger
		self.vpn_gateway = vpn_gateway
		self.metric_service = metric_service

	def get_dapp_status(self):
		state_name = 'ACTIVE'

		try:
			server_stats = self.vpn_gateway.get_status()
		except Exception as e:
			server_stats = {}
			state_name = 'INACTIVE'
			self.logger.error('VPNStatusService::dapp_status: Failed to obtain OpenVPN server status')

		try:
			metrics_stats = self.metric_service.get_current_metrics()
		except Exception as e:
			metrics_stats = {}
			metrics_stats = 'INACTIVE'
			self.logger.error('VPNStatusService::dapp_status: Failed to obtain OpenVPN network device status')

		return {**server_stats, 'metrics_stats': metrics_stats, 'state_name': state_name}
