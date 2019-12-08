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
			return self._unserialize(self.gw.client.get('mnlist:entry:' + ip).decode('utf-8'))
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

	def exists(self, ip):
		return ('mnlist:entry:' + ip) in self.data

	def delete(self, ip):
		self.data.pop('mnlist:entry:' + ip)

	def _serialize(self, obj):
		return pickle.dumps(obj)

	def _unserialize(self, dump):
		return pickle.loads(dump)



class MetricRepository(object):
	""" Does CRUD operation with Metric object on Redis database """

	def __init__(self, redis_gateway):
		"""Constructor"""
		self.gw = redis_gateway

	def store(self, key, value):
		self.gw.client.set('metric:entry:' + key, self._serialize(value))

	def get(self, key):
		if self.exists(key):
			return self._unserialize(self.gw.client.get('metric:entry:' + key))	#.decode('utf-8'))
		return None

	def get_all(self):
		keys = self.get_keys()
		data = self.gw.client.mget(keys)
		result = {}

		for i in range(len(keys)):
			result[keys[i]] = self._unserialize(data[i])

		return result

	def get_keys(self):
		cursor, keys = self.gw.client.scan(match='metric:entry:*')
		return keys

	def exists(self, key):
		return self.gw.client.get('metric:entry:' + key) is not None

	def delete(self, key):
		self.data.pop(key)

	def _serialize(self, obj):
		return pickle.dumps(obj)

	def _unserialize(self, dump):
		return pickle.loads(dump)

