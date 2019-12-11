""" Job to perform MN service discovery """

import requests, json, time, asyncio

class DiscoveryDaemon(object):
	"""Service to manage extended masternode sync"""
	def __init__(self, config, logger, mnsync_service, masternode_gateway):
		"""Constructor"""
		self.mnsync_service = mnsync_service
		self.logger = logger
		self.config = config
		self.gw = masternode_gateway

	def start_job(self):
		""" Starts service discovery job """
		loop = asyncio.get_event_loop()
		loop.run_until_complete(asyncio.gather(
			self.service_discovery_task()
			))
		loop.run_forever()

	@asyncio.coroutine
	def service_discovery_task(self):
		pref = 'DiscoveryDaemon::service_discovery_task: '
		self.logger.info(pref + 'Starting asynchronous service_discovery_task')

		while True:
			self.logger.debug(pref + '[ sleeping for %i s ]' % int(self.config['discovery'].get('discovery_delay', 300)))
			yield from asyncio.sleep(int(self.config['discovery'].get('discovery_delay', 300)))
			self.logger.debug(pref + 'Starting full masternode service discovery ...')

			try:
				self.do_service_discovery()

			except Exception as e:
				self.logger.error(pref + 'Error: [task will restart]: ' + str(e))
				continue

	def do_service_discovery(self):
		mn_list = self.mnsync_service.get_core_masternode_list('full')
		pref = "DiscoveryDaemon::do_service_discovery"

		if not mn_list:
			self.logger.error(pref + "Error: Failed to fetch masternode list from core node")

		for ip, mn in mn_list.items():
			self.logger.debug(pref + ': query ' + mn.ip)
			query = self.gw.webapi_query(mn.ip, 'status')

			if query.success:
				if 'services' in query.result and 'blockchain' in query.result and 'masternode' in query.result:
					mn.status = 'ACTIVE'

					mn.update_service_info({
						'services_available': list(query.result['services'].keys()),
						'api_latency': query.latency
					})

					if 'signing_key' in query.result['masternode']:
						mn.signing_key = query.result['masternode']['signing_key']

				if 'version' in query.result and 'api_version' in query.result['version']:
					mn.update_version_info({
						'api_version': query.result['version']['api_version'],
						'core_version': query.result['version']['core_version'],
						'mn_version': query.result['version']['mn_version'],
						'protocol_version': query.result['version']['protocol_version'],
					})
				elif 'blockchain' in query.result and 'api_version' in query.result['blockchain']:	# older MN2 nodes
					mn.update_version_info({
						'api_version': query.result['blockchain']['api_version'],
						'core_version': query.result['blockchain']['core_version'],
						'mn_version': query.result['blockchain']['mn_version'],
						'protocol_version': query.result['blockchain']['protocol_version'],
					})

			else:
				mn.update_service_info({
					'services': [],
				})

			self.mnsync_service.update_masternode_list(mn)
