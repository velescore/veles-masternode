#!/usr/bin/env python
import velesrpc
import asyncio, sys, json, configparser, requests
from aiohttp import web

class VelesMNWebSync(object):
	headers = {"Server": "VelesMNWebSync"}
	lists = {"masternodes": {}, "providers": {}}

	def __init__(self, config_path='/etc/veles/webserver.conf'):
		self.configparser = configparser.ConfigParser()
		self.configparser.read(config_path)
		self.daemon = velesrpc.VelesRPCClient(
			self.config('rpchost', '127.0.0.1', 'veles_wallet'),
			self.config('rpcport', '21337', 'veles_wallet'),
			self.config('rpcuser', None, 'veles_wallet'),
			self.config('rpcpassword', None, 'veles_wallet'),
			)

	def config(self, key, default = None, section = 'mn_web_sync'):
		try:
			return self.configparser[section].get(key, default)
		except:
			return default

	def send_service_query(self, node_ip, method = 'status', api_dir = 'api'):
		url = 'https://%s/%s/%s' % (node_ip, api_dir, method)

		try:
			response = requests.get(url, headers=self.headers, verify=False, timeout=int(self.config('query_timeout', 10)))	#self.config('ca_cert', '/etc/veles/vpn/keys/ca.crt'))

			if 'error' in response.json() and response.json()['error'] != None:
				return False

			result = response.json()['result']
		except:
			return False

		return result

	def discover_all_services(self):
		mn_list = self.daemon.rpc_call('masternodelist', ['addr'])

		for output, mn_addr in mn_list.items():
			mn_ip, mn_port = mn_addr.split(':')
			#mn_ip = '127.0.0.1'
			print('Checking masternode %s' % mn_ip)
			status = self.send_service_query(mn_ip + ':21339')	#('80.211.5.147')

			try:
				status_name = self.daemon.rpc_call('masternodelist', ['status', output])[output]
			except:
				status_name = 'UNKNOWN'

			if mn_ip not in self.lists['masternodes']:
				print('Found new Masternode %s' % mn_ip)
				self.lists['masternodes'][mn_ip] = {'state_name': status_name}

			if status:
				self.lists['masternodes'][mn_ip]['status'] = status

			if status and 'services' in status:
				for service in status['services'].keys():
					if service not in self.lists['providers']:
						self.lists['providers'][service] = []

					if mn_ip not in self.lists['providers'][service]:
                                                self.lists['providers'][service] += [mn_ip]


	@asyncio.coroutine
	def service_discovery_task(self):
		while True:
			print('Starting new complete service discovery ...')
			self.discover_all_services()
			print(self.lists)
			yield from asyncio.sleep(self.config('discovery_delay', 10))

	def run(self):
		loop = asyncio.get_event_loop()
		#try:
		loop.run_until_complete(asyncio.gather(
			self.service_discovery_task()
			))
		loop.run_forever()
		#except KeyboardInterrupt:
		#	print("\n* Shutting down on keyboard interrupt *")
		#except:
		#	print("\n* Shutting down on error")



# Self-test, basic commandline interface
def main():
	if len(sys.argv) == 2 and sys.argv[1] == '--help':
		print("Veles MN Web Sync\nUsage: %s [config]\n" % sys.argv[0])
		return

	if len(sys.argv) > 1:
		server = VelesMNWebSync(sys.argv[1])
	else:
		server = VelesMNWebSync()

	server.run()

if __name__=='__main__':
	main()


