#!/usr/bin/env python

import importlib

class dAppRegistry(object):
	dapp_facades = {}

	def __init__(self, config, logger):
		self.config = config
		self.logger = logger

	def register_dapp(self, dapp_provider):
		# todo: do assertions on object base class type
		if dapp_provider.name() in self.dapp_facades:
			self.logger.warning('dAppRegistry::register_dapp: dApp %s is already registered' % dapp_provider.name())

		self.logger.debug('dAppRegistry::register_dapp: Registering dApp %s' % dapp_provider.name())
		self.dapp_facades[dapp_provider.name()] = dapp_provider.make_facade()

	def load_dapps(self, container):
		modules = {}

		for dapp_name in self.config['dapps'].get('enabled').split(','):
			modules[dapp_name.strip()] = importlib.import_module("dapps.vpn.provider")
			self.register_dapp(modules[dapp_name.strip()].dAppProvider(container))

	def get_all(self):
		return self.dapp_facades

	def get_names(self):
		return self.dapp_facades.keys()
