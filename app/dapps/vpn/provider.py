#!/usr/bin/env python

from dapps.interfaces import AbstractProvider
from dapps.vpn import facade
from dapps.vpn import status_service
from dapps.vpn import metric_service

class dAppProvider(AbstractProvider):
	dapp_name = 'VPN'
	dependencies = {}
	db_type = 'mem'
	gw_type = 'dummy'

	def __init__(self, container):
		self.container = container

	def name(self):
		return self.dapp_name

	def register(self, name, dependency):
		if not name in self.dependencies:
			self.dependencies[name] = dependency

	def singleton(self, name):
		if name in self.dependencies:
			return self.dependencies[name]
		return None

	def make_facade(self):
		if self.gw_type == 'dummy':
			from dapps.vpn import dummy

			self.register('DummyVPNManagementGateway', dummy.DummyVPNManagementGateway())
		else:
			from dapps.vpn import gateway

			self.register('VPNManagementGateway', gateway.VPNManagementGateway(
					config=self.container.app_config(), 
					logger=self.container.logger(),
					))

		self.register('VPNMetricService', metric_service.VPNMetricService(
				config=self.container.app_config(), 
				logger=self.container.logger(),
				metric_repository=self.container.metric_repository(),
				))
		self.register('VPNStatusService', status_service.VPNStatusService(
				config=self.container.app_config(), 
				logger=self.container.logger(),
				vpn_gateway=self.singleton('VPNManagementGateway'),
				metric_service=self.singleton('VPNManagementGateway'),
				))

		# Return main dApp facade that will act as API between other
		# parts of system and internal services registered here.
		return facade.VPNdAppFacade(
			config=self.container.app_config(), 
			logger=self.container.logger(),
			status_service=self.singleton('VPNStatusService'),
			metric_service=self.singleton('VPNMetricService')
			)