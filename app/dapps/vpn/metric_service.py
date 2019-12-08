#!/usr/bin/env python
from dapps.interfaces import AbstractMetricService
from datetime import datetime, timedelta

class VPNMetricService(AbstractMetricService):
	data_prefix = 'vpn'
	intervals = {
		'hourly': 3600,
		'daily': 3600*24
	}

	def __init__(self, config, logger, metric_repository):
		""" Constructor """
		self.config = config
		self.logger = logger
		self.repo = metric_repository

	def get_recent_metrics(self, interval_name):
		""" Retrieves metrics for the last specified time interval """
		if not interval_name in self.intervals:
			self.logger.warning('VPNMetricService::update_recent_metrics: Unsupported interval ' + interval_name)
			return

		now = datetime.now()

		if interval_name == 'hourly':
			key_timeformat = "hourly:%m-%d_%H"
			last_time = now - timedelta(hours=1)
			last_time_since = last_time - timedelta(hours=1)
		elif interval_name == 'daily':
			key_timeformat = "daily:%m-%d"
			last_time = now - timedelta(days=1)
			last_time_since = last_time - timedelta(days=1)
		else:
			return {}	# this should not happen

		last_metrics_key = '%s:%s' % (self.data_prefix, last_time.strftime(key_timeformat))

		if not self.repo.exists(last_metrics_key):
			self.logger.info('VPNMetricService::get_recent_metrics: No recent metrics in database for interval ' + interval_name)
			return {}

		return self.repo.get(last_metrics_key)


	def update_recent_metrics(self, interval_name):
		""" Calculates and updates metrics for the last specified time interval """
		if not interval_name in self.intervals:
			self.logger.warning('VPNMetricService::update_recent_metrics: Unsupported interval ' + interval_name)
			return

		now = datetime.now()

		if interval_name == 'hourly':
			key_timeformat = "hourly:%m-%d_%H"
			prev_time = now - timedelta(hours=1)
		elif interval_name == 'daily':
			key_timeformat = "daily:%m-%d"
			prev_time = now - timedelta(days=1)
		else:
			self.logger.debug('VPNMetricService::update_recent_metrics: No action for interval ' + interval_name)
			return

		prev_metrics_key = '%s:%s' % (self.data_prefix, prev_time.strftime(key_timeformat))
		cur_metrics_key = '%s:%s' % (self.data_prefix, now.strftime(key_timeformat))
		cur_metrics_state = self._get_current_metrics()

		self.repo.store(cur_metrics_key + ':state', cur_metrics_state)

		if self.repo.exists(prev_metrics_key + ':state'):
			prev_metrics_state = self.repo.get(prev_metrics_key + ':state')

		else:
			self.logger.debug('VPNMetricService::update_recent_metrics: No previous metric records found for interval ' + interval_name)
			return

		self.repo.store(prev_metrics_key, {
			'interval_since': prev_time.isoformat().split('.')[0],	# remove miliseconds
			'interval_until': now.isoformat().split('.')[0],
			**self._compare_metrics(prev_metrics_state, cur_metrics_state)
			})

	# Private methods
	def _get_current_metrics(self):
		interface = self.config['dapps.vpn'].get('tun_interface', 'tun1')
		bytes_in, bytes_out = self._get_network_bytes(interface)
		return { 'bytes_in': bytes_in, 'bytes_out': bytes_out}

	def _compare_metrics(self, previous_metrics, current_metrics):
		try:
			if current_metrics['bytes_in'] < previous_metrics['bytes_in'] or current_metrics['bytes_out'] < previous_metrics['bytes_out']:
				self.logger.info('VPNMetricService::_compare_metrics: VPN metrics have been reset within last hour, not enough data')
				return { 'bytes_in': 0, 'bytes_out': 0}

			return {
				'bytes_in': current_metrics['bytes_in'] - previous_metrics['bytes_in'],
				'bytes_out': current_metrics['bytes_out'] - previous_metrics['bytes_out'],
			}
		except Exception as e:
			raise Exception('VPNMetricService::_compare_metrics: Failed to compare given metrics: ' + str(e))

	def _get_network_bytes(self, interface):
		for line in open('/proc/net/dev', 'r'):
			if interface in line:
				data = line.split('%s:' % interface)[1].split()
				rx_bytes, tx_bytes = (data[0], data[8])
				return (int(rx_bytes), int(tx_bytes))
		raise Exception('VPNMetricService::_get_network_bytes: Network interface not found: ' + interface)
