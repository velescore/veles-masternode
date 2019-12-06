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

		self.dapp_facades[dapp_provider.name()] = dapp_provider.make_facade(container)
		self.logger.debug('dAppRegistry::register_dapp: Registered dApp %s' % dapp_provider.name())

	def load_dapps(self, container):
		providers = {}

		for dapp_name in self.config['dapps'].get('enabled').split(','):
			dapp_name = dapp_name.strip()

			providers[dapp_name] = importlib.import_module("dapps.vpn.provider")
			dapp_provider = providers[dapp_name].dAppProvider()
			self.dapp_facades[dapp_name] = dapp_provider.make_facade(container)

	def get_all(self):
		return self.dapp_facades

	def get_names(self):
		return self.dapp_facades.keys()
