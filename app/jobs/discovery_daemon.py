""" Job to perform MN service discovery """

import requests, json, time, asyncio

class DiscoveryDaemon(object):
	"""Service to manage extended masternode sync"""
	headers = {"Server": "Veles Core Masternode (DiscoveryDaemon)"}

	def __init__(self, mnsync_service, logger, config):
		"""Constructor"""
		self.mnsync_service = mnsync_service
		self.logger = logger
		self.config = config

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
			dapp_status, service_latency = self.query_dapp_status(ip)

			if dapp_status and 'services' in dapp_status:
				mn.update_service_info({
					'services': list(dapp_status['services'].keys()),
					'dapp_status': 'ENABLED',
					'latency_ms': service_latency
				})
				if 'blockchain' in dapp_status and 'api_version' in dapp_status['blockchain']:
					mn.update_version_info({
						'api_version': dapp_status['blockchain']['api_version'],
						'core_version': dapp_status['blockchain']['core_version']
					})
			else:
				mn.update_service_info({
					'services': [],
					'dapp_status': 'INACTIVE',
					'latency_ms': service_latency
				})

			self.mnsync_service.update_masternode_list(mn)

	def query_dapp_status(self, node_ip, method = 'status', api_dir = 'api'):
		url = 'https://%s/%s/%s' % (node_ip, api_dir, method)
		request_start = time.time()

		try:
			response = requests.get(url, headers=self.headers, verify=self.config['discovery'].get('ca_cert', False), timeout=int(self.config['discovery'].get('query_timeout', 10)))	#self.config['discovery'].get('ca_cert', '/etc/veles/vpn/keys/ca.crt'))

			if 'error' in response.json() and response.json()['error'] != None:
				return False

			result = response.json()['result']

		except Exception as e:
			self.logger.error('DiscoveryDaemon::query_dapp_status: Error: ' + str(e))
			result = False

		request_end = time.time()

		return result, round((request_end - request_start) * 1000)







		
