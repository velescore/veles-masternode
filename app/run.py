#!/usr/bin/env python3

""" Command-line interface to the main masternode app """

import argparse

from container import IocContainer

class VelesMasternodeCLI(object):
	def run(self):
		""" Run the commandline interface """
		args = self.get_args()
		container = self.get_container(args)
		container.app().init_dapps(container)
		container.app().run_job(args['action'])

	def get_args(self):
		""" Proccess commandline args if not done yet, exit with help on errors """
		parser = argparse.ArgumentParser(description='Veles Core Masternode Manager version {} *EXPERIMENTAL*'.format('0.18.3'))
		parser.add_argument('action', help="Action to perform")
		parser.add_argument('--config', default='/etc/veles/mn.conf', help='Specify Veles Masternode configuration file.')
		return vars(parser.parse_args())

	def get_container(self, args):
		return IocContainer(
			config=args	# Container's initial parameters, configuration to load real config
		)

if __name__ == '__main__':
	app = VelesMasternodeCLI()
	app.run()

