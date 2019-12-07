""" Veles Masternode (gen 2) masternode models """

from masternode.base import BaseFillableObject
import copy

class Masternode(BaseFillableObject):
	""" Represents a last known state of a masternode """
	_required = ['ip', 'outpoint', 'payee']		# Required attributes
	dapp_status = 'UNKNOWN'
	core_info = {}
	service_info = {}
	version_info = {}
	last_checked = None

	def update_core_info(self, core_info):
		self.core_info.update(core_info)

	def update_service_info(self, service_info):
		self.service_info.update(service_info)

	def update_version_info(self, version_info):
		self.version_info.update(version_info)

	def attributes(self):
		info = self.__dict__
		
		# Todo: make this in base class from like _nested = ['version_info', ...]
		info.update(self.version_info)
		info.update(self.core_info)
		info.update(self.service_info)

		if 'version_info' in info:
			info.pop('version_info')

		if 'core_info' in info:
			info.pop('core_info')

		if 'service_info' in info:
			info.pop('service_info')

		return info

