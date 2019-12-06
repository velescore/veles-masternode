#!/usr/bin/env python

class VPNdAppFacade(object):
	app_name = 'VPN'

	def __init__(self, config, logger, status_service):
		self.config = config
		self.logger = logger
		self.logger.debug('VPNdAppFacade: dVPN dApp loaded')
		self.status_service = status_service

	def service_status(self):
		return self.status_service.service_status()

