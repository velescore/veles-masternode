""" Masternode object repository """

#import redis

class RedisGateway(object):
	def __init__(self, host, port, db = 0):
		#self.client = redis.Redis(host = host, port = port, db = db)
		return

class MasternodeRepository(object):
	""" Does CRUD operation with Masternode object on Redis database """

	def __init__(self, redis_gateway):
		"""Constructor"""
		self.gateway = redis_gateway

	def set(self, command, args = []):
		"""For debugging porposes"""
		return (command, args)
		