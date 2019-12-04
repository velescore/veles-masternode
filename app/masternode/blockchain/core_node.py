"""Module to handle communication with wallet/node daemon"""

import requests, json, configparser, itertools

class CoreNodeService(object):
	"""Service to communicate with the Veles Core daemon"""

	def __init__(self, config, logger):
		"""Constructor"""
		self.core_node = CoreNodeRPCClient(
	        host=config['wallet'].get('rpchost', '127.0.0.1'),
	        port=config['wallet'].get('rpcport', '21338'),
	        username=config['wallet'].get('rpcuser'),
	        password=config['wallet'].get('rpcpassword'),
	        )
		self.config = config
		self.logger = logger

	def command(self, command, args = []):
		"""For debugging porposes"""
		return self.core_node.call(command, args)
		
class CoreNodeRPCClient(object):
	def __init__(self, host = "127.0.0.1", port = 25522, username = None, password = None):
		self.host = host
		self.port = int(port)
		self.username = username
		self.password = password

	def call(self, method, params = []):
		if self.username or self.password:
			url = "http://%s:%s@%s:%s" % (self.username, self.password, self.host, self.port)
		else:
			url = "http://%s:%s/" % (self.host, self.port)

		headers = {
			'content-type': 'application/json'
			}
		payload = {
			"method": method,
			"params": params,
			"jsonrpc": "1.0",
			"id": 0
		}
		response = requests.post(url, data=json.dumps(payload), headers=headers)
		try:
			if 'error' in response.json() and response.json()['error'] != None:
				return response.json()	#False

			if 'result' in response.json():
				return response.json()['result']

		except:
			return response.text


		
