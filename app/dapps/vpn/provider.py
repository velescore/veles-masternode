#!/usr/bin/env python

from dapps.vpn import facade
from dapps.vpn import status

class dAppProvider(object):
	dapp_name = 'VPN'

	def name(self):
		return self.dapp_name

	def make_facade(self, container):
		return facade.VPNdAppFacade(
			config=container.app_config(), 
			logger=container.logger(),
			status_service=status.VPNStatusService(
				config=container.app_config(), 
				logger=container.logger(),
				)
			)