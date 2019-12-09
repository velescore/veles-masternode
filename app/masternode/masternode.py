""" Veles Masternode (gen 2) masternode models """
from masternode.interfaces import AbstractFillableObject
import copy

class Masternode(AbstractFillableObject):
	""" Represents a masternode """
	_required = ['ip', 'outpoint', 'payee']		# Required attributes
	dapp_status = 'UNKNOWN'
	last_checked = None
	signing_key = None


class CoreInfoMixin(object):
	""" Adds core daemon information about the masternode """
	_core_info = {}

	def update_core_info(self, core_info):
		self._core_info.update(core_info)

	def get_core_info(self):
		return self._core_info

	def attributes(self):
		return {**super().attributes(), **self._core_info}


class VersionInfoMixin(object):
	""" Adds version information about the masternode """
	_version_info = {}

	def update_version_info(self, version_info):
		self._version_info.update(version_info)

	def get_version_info(self):
		return self._version_info

	def attributes(self):
		return {**super().attributes(), **self._version_info}


class ServiceInfoMixin(object):
	""" Adds service information about the masternode """
	_service_info = {}

	def update_service_info(self, service_info):
		self._service_info.update(service_info)

	def get_service_info(self):
		return self._service_info

	def attributes(self):
		return {**super().attributes(), **self._service_info}


class MasternodeInfo(ServiceInfoMixin, VersionInfoMixin, CoreInfoMixin, Masternode):
	""" Represents a last known state of a masternode with associated information """
	pass
