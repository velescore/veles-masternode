#!/usr/bin/env python3

"""Runs the blockchain orchestration script"""

import sys, logging, argparse

from container import IocContainer

class VelesMasternodeCLI(object):
	_container = None
	_args = {}

	def run(self):
		""" Run the commandline interface """
		#try:		# Uncomment in production!
		self.init_args()
		self.init_container()
		self._container.run_job(self._args['action'])

		#except KeyboardInterrupt:
		#	print("\nVelesMasternodeCLI: Shutting down on keyboard interrupt\n")

		#except Exception as e:	# Print an error instead of leaking stack trace etc.
		#	print('Error: ' + str(e))

	def init_args(self):
		""" Proccess commandline args if not done yet, exit with help on errors """
		parser = argparse.ArgumentParser(description='Veles Core Masternode Manager version {} *EXPERIMENTAL*'.format('0.18.3'))
		parser.add_argument('action', help="Action to perform")
		parser.add_argument('--config', default='/etc/veles/mn.conf', help='Specify Veles Masternode configuration file.')
		self._args = vars(parser.parse_args())

	def init_container(self):
		self._container = IocContainer(
			config=self._args	# Container's initial parameters, configuration to load real config
		)
		self._container.logger().addHandler(logging.StreamHandler(sys.stdout))

if __name__ == '__main__':
	app = VelesMasternodeCLI()
	app.run()

