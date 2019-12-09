""" Veles Masternode (gen 2) sync service """

from masternode.masternode import MasternodeInfo

class MasternodeSyncService(object):
	"""Service to manage extended masternode sync"""

	def __init__(self, masternode_repo, core_node_service, logger):
		"""Constructor"""
		self.mn_repo = masternode_repo
		self.core_node = core_node_service
		self.logger = logger

	def get_masternode_list(self, mode = None):
		""" Returns masternode list, whether core or extended """
		if mode == 'full':
			core_list = self.get_core_masternode_list('full')
			stored_list = self.mn_repo.get_all()

			for ip, mn in stored_list:
				if ip in core_list:
					stored_list[ip].update_core_info(core_list[ip].get_core_info())

			return stored_list

		else:
			return self.mn_repo.get_all()

		self.logger.warning('MasternodeSyncService::get_masternode_list(): unknown mode "%s"' % mode)
		return False

	def get_core_masternode_list(self, mode = None):
		""" Returns masternode list """
		try:
			raw_list = self.core_node.call('masternodelist', [mode])
		except:
			self.logger.warning('MasternodeSyncService::get_masternode_list(): failed to obtain masternode list "%s" from core_node' % mode)
			return False

		return self.parse_core_mnlist(raw_list, mode)
		
	def update_masternode_list(self, masternode):
		self.mn_repo.store(masternode)

	def parse_core_mnlist(self, mn_list, mode = 'full', reindex_by = None, dictionary = False):
		mode_keys = {
			'addr': ['addr'],
			'full': ['status', 'protocol', 'payee', 'last_seen', 'active_seconds', 'last_paid_time' ,'last_paid_block', 'addr']
		}
		extra_keys = ['ip', 'outpoint']
		result = {}
		key = 'ip'
		core_default_key = 'outpoint'

		if reindex_by:
			key = reindex_by

		if not mode in mode_keys:
			raise ValueError('MasternodeSyncService::parse_core_mnlist(): unsupported mode ' + mode)

		if not key in mode_keys[mode] and key not in extra_keys:
			raise ValueError('MasternodeSyncService::parse_core_mnlist(): unsupported key type ' + key)

		for outpoint, info_str in mn_list.items():
			if not info_str:
				continue

			info = info_str.split()
			entry = {core_default_key: outpoint}

			if len(info) != len(mode_keys[mode]):
				self.logger.info('Got incomplete masternode info from core_node list "%s": %s' % (mode, outpoint))
				continue

			for i in range(0, len(info)):
				field_value = info[i]
				field_name = mode_keys[mode][i]
				entry[field_name] = field_value

				# Transform addr to IP, port stays always the same
				if field_name == 'addr':
					entry['ip'] = field_value.split(':')[0]
					entry.pop('addr')

			if dictionary or mode != 'full':
				result[entry[key]] = entry
			else:
				result[entry[key]] = MasternodeInfo({
					'ip': entry['ip'],
					'outpoint': entry['outpoint'],
					'payee': entry['payee']
					})
				result[entry[key]].update_core_info(entry)

		return result