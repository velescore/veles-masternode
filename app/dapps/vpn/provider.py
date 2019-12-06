#!/usr/bin/env python

from dapps.vpn import facade
from dapps.vpn import status

class dAppProvider(object):
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
		# Lazy load only when needed first time
		if self.db_type == 'redis':
			from persistence.repsitory import redis

			self.register('StatsRepository', redis.StatsRepository(
					redis_gateway=self.container.redis_gateway(),
					prefix='dapp.vpn'
					))
		else:
			from persistence.repository import mem

			self.register('StatsRepository', mem.StatsRepository())

		if self.gw_type == 'dummy':
			from dapps.vpn import dummy

			self.register('DummyVPNManagementGateway', dummy.DummyVPNManagementGateway())
		else:
			from dapps.vpn import gateway

			self.register('VPNManagementGateway', gateway.VPNManagementGateway(
					config=self.container.app_config(), 
					logger=self.container.logger(),
					))


		self.register('VPNStatusService', status.VPNStatusService(
				config=self.container.app_config(), 
				logger=self.container.logger(),
				vpn_gateway=self.singleton('VPNManagementGateway'),
				stats_repo=self.singleton('StatsRepository'),
				))

		# Return main dApp facade that will act as API between other
		# parts of system and internal services registered here.
		return facade.VPNdAppFacade(
			config=self.container.app_config(), 
			logger=self.container.logger(),
			status_service=self.singleton('VPNStatusService')
			)