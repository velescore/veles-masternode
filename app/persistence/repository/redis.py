""" Redis repositorires """

import redis, pickle


""" Masternode object repository """

#import redis

class RedisGateway(object):
	def __init__(self, config):
		self.client = redis.Redis(
                    host = config['redis'].get('host', '127.0.0.1'),
                    port = config['redis'].get('port', '21345'),
                    db = config['redis'].get('db', '0')
                )

class MasternodeRepository(object):
	""" Does CRUD operation with Masternode object on Redis database """

	def __init__(self, redis_gateway):
		"""Constructor"""
		self.gw = redis_gateway

	def store(self, mn):
		self.gw.client.set('mnlist:entry:' + mn.ip, self._serialize(mn))

	def get(self, ip):
		if self.exists(ip):
			return self.unserialize(self.gw.client.get('mnlist:entry:' + ip).decode('utf-8'))
		return None

	def get_all(self):
		keys = self.get_keys()
		data = self.gw.client.mget(keys)
		result = {}

		for i in range(len(keys)):
			result[keys[i]] = self._unserialize(data[i])

		return result

	def get_keys(self):
		cursor, keys = self.gw.client.scan(match='mnlist:entry:*')
		return keys

	def exists(self, key):
		return key in self.data

	def delete(self, key):
		self.data.pop(key)

	def _serialize(self, obj):
		return pickle.dumps(obj)

	def _unserialize(self, dump):
		return pickle.loads(dump)



class StatsRepository(object):
	""" Does CRUD operation with Masternode object on Redis database """

	def __init__(self, redis_gateway, prefix='mn'):
		"""Constructor"""
		self.gw = redis_gateway
		self.prefix = 'stats:' + prefix

	def store(self, mn):
		self.gw.client.set(self.prefix + ':entry:' + mn.ip, self._serialize(mn))

	def get(self, ip):
		if self.exists(ip):
			return self.unserialize(self.gw.client.get(self.prefix + ':entry:' + ip).decode('utf-8'))
		return None

	def get_all(self):
		keys = self.get_keys()
		data = self.gw.client.mget(keys)
		result = {}

		for i in range(len(keys)):
			result[keys[i]] = self._unserialize(data[i])

		return result

	def get_keys(self):
		cursor, keys = self.gw.client.scan(match=self.prefix + ':entry:*')
		return keys

	def exists(self, key):
		return key in self.data

	def delete(self, key):
		self.data.pop(key)

	def _serialize(self, obj):
		return pickle.dumps(obj)

	def _unserialize(self, dump):
		return pickle.loads(dump)

