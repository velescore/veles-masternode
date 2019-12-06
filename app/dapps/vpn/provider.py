#!/usr/bin/env python

from dapps.vpn import facade
from dapps.vpn import status
from dapps.vpn import gateway

class dAppProvider(object):
	dapp_name = 'VPN'
	dependencies = {}

	def name(self):
		return self.dapp_name

	def register(self, name, dependency):
		if not name in self.dependencies:
			self.dependencies[name] = dependency

	def singleton(self, name):
		if name in self.dependencies:
			return self.dependencies[name]
		return None

	def make_facade(self, container):
		# Lazy load when needed first time
		self.register('VPNManagementGateway', gateway.VPNManagementGateway(
				config=container.app_config(), 
				logger=container.logger(),
				))
		self.register('VPNStatusService', status.VPNStatusService(
				config=container.app_config(), 
				logger=container.logger(),
				vpn_gateway=self.singleton('VPNManagementGateway'),
				))

		# Return main dApp facade that will act as API between other
		# parts of system and internal services registered here.
		return facade.VPNdAppFacade(
			config=container.app_config(), 
			logger=container.logger(),
			status_service=self.singleton('VPNStatusService')
			)