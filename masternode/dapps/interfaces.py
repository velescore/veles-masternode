#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

class AbstractProvider(object, metaclass=ABCMeta):
	@abstractmethod
	def make_facade(self):
		""" Returns facade to the provided service as child of dapps.AbstractFacade """
		pass

class AbstractFacade(object, metaclass=ABCMeta):
	app_name = None

	def __init__(self, config, logger):
		self.config = config
		self.logger = logger

	@abstractmethod
	def get_status_service(self):
		pass

	@abstractmethod
	def get_metric_service(self):
		pass

	def name():
		return self.app_name

class AbstractMetricService(object, metaclass=ABCMeta):
	@abstractmethod
	def get_recent_metrics(self, interval_name):
		""" Calculates and updates in database metrics for the last specified time interval """
		pass
	@abstractmethod
	def update_recent_metrics(self, interval_name):
		""" Calculates and updates metrics for the last specified time interval """
		pass

class AbstractGlobalMetricService(AbstractMetricService, metaclass=ABCMeta):
	@abstractmethod
	def get_global_metrics(self, interval_name):
		""" Calculates and updates in database metrics for the last specified time interval """
		pass
	@abstractmethod
	def update_global_metrics(self, interval_name):
		""" Calculates and updates metrics for the last specified time interval """
		pass

class AbstractStatusService(object, metaclass=ABCMeta):
	@abstractmethod
	def get_dapp_status(self):
		""" Returns stats information of current dApp as dictionary """
		pass
