#!/usr/bin/env python

class VPNStatusService(object):
	def __init__(self, config, logger):
		self.config = config
		self.logger = logger

	def service_status(self):
		return {'coolness': 65535}

