""" Job to perform MN service discovery """

import asyncio, time

class MetricDaemon(object):
	"""Service to manage extended masternode sync"""
	headers = {"Server": "Veles Core Masternode (MetricDaemon)"}
	intervals = {
		'hourly': 3.600,
		'daily': 3.600*24
	}

	def __init__(self, config, logger, metric_repository, dapp_registry):
		"""Constructor"""
		self.repo = metric_repository
		self.logger = logger
		self.config = config
		self.dapps = dapp_registry.get_all()

	def start_job(self):
		""" Starts service discovery job """
		loop = asyncio.get_event_loop()
		loop.run_until_complete(asyncio.gather(
			self.recent_metrics_update_task('hourly'),
			self.recent_metrics_update_task('daily')
			))
		loop.run_forever()

	@asyncio.coroutine
	def recent_metrics_update_task(self, interval_name):
		pref = 'MetricDaemon::recent_metrics_update_task [%s]: ' % interval_name
		interval = self.intervals[interval_name]
		self.logger.info(pref + 'Starting new asynchronous task')
		next_sleep_seconds = interval

		while True:
			self.logger.debug(pref + '[ sleeping for %i s / running %s ]' % (next_sleep_seconds, interval_name))
			yield from asyncio.sleep(next_sleep_seconds)

			action_started_at = time.time()
			#try:
			self.update_recent_metrics(interval_name)

			#except Exception as e:
			#	self.logger.error(pref + 'Error: [task will restart]: ' + str(e))
			#	continue

			action_duration = time.time() - action_started_at

			if action_duration > interval:
				next_sleep_seconds = 0
				self.logger.warning(pref + "Action took longer than it's schedule! [ took %is / scheduled %s ]" % (
					action_duration,
					interval_name
					))
			else:
				next_sleep_seconds = interval - action_duration

	def update_recent_metrics(self, interval_name):
		for dapp_name, dapp_facade in self.dapps.items():
			self.logger.debug('MetricDaemon::update_recent_metrics: Updating %s metrics of dApp %s' % (interval_name, dapp_name))
			dapp_facade.get_metric_service().update_recent_metrics(interval_name)
			dapp_facade.get_metric_service().get_recent_metrics(interval_name)