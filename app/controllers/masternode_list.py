#!/usr/bin/env python
import asyncio, sys, json, version
from controllers.interfaces import AbstractSigningController

class MasternodeListController(AbstractSigningController):
	def __init__(self, config, logger, signing_service, mnsync_service):
		super().__init__(config, logger, signing_service)
		self.mnsync_service = mnsync_service

	@asyncio.coroutine
	def handle(self, request):
		try:
			mn_list = self.mnsync_service.get_masternode_list()
		except Exception as e:
			self.logger.error('Failed to obtain masternode list: ' + str(e))
			return self.error_response('Failed to obtain masternode list', 559)	# first 4 letters of "wallet" on T9 keyboard

		return self.response(self._normalize(mn_list))

	def _normalize(self, mn_list):
		result = {}

		for ip, mn in mn_list.items():
			result[ip] = mn.attributes()

		return result
