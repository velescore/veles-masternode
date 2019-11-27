#!/usr/bin/env python
import velesrpc, redis
import asyncio, sys, json, configparser, requests, time
from aiohttp import web

class VelesMNWebSync(object):
	headers = {"Server": "VelesMNWebSync"}
	lists = {"masternodes": {}, "svc_providers": {}}

	def __init__(self, config_path='/etc/veles/webserver.conf'):
		self.configparser = configparser.ConfigParser()
		self.configparser.read(config_path)
		self.daemon = velesrpc.VelesRPCClient(
			self.config('rpchost', '127.0.0.1', 'veles_wallet'),
			self.config('rpcport', '{{svc-port:system.wallet.velesCoreDaemon}}', 'veles_wallet'),
			self.config('rpcuser', None, 'veles_wallet'),
			self.config('rpcpassword', None, 'veles_wallet')
		)
		self.redis = redis.Redis(
			host=self.config('host', '127.0.0.1', 'redis_db'),
			port=self.config('port', '{{svc-port:system.db.redisServer}}', 'redis_db'),
			db=self.config('db', '0', 'redis_db')
		)

	def config(self, key, default = None, section = 'mn_web_sync'):
		try:
			return self.configparser[section].get(key, default)
		except:
			return default

	def send_service_query(self, node_ip, method = 'status', api_dir = 'api'):
		url = 'https://%s/%s/%s' % (node_ip, api_dir, method)

		try:
			response = requests.get(url, headers=self.headers, verify=self.config('ca_cert', False), timeout=int(self.config('query_timeout', 10)))	#self.config('ca_cert', '/etc/veles/vpn/keys/ca.crt'))

			if 'error' in response.json() and response.json()['error'] != None:
				return False

			result = response.json()['result']
		except KeyboardInterrupt:
			print("Shutting down on keyboard interrupt")
			sys.exit()
		except:
			return False

		return result

	def discover_all_services(self):
		mn_list = self.daemon.rpc_call('masternodelist', ['full'])
		#mn_ranks = self.daemon.rpc_call('masternodelist', ['rank'])
		mn_ips = []
		old_mn_ips = []
		dapp_support_ips = []
		#a = 0

		# Load the old list from redis database
		for i in range(0, self.redis.llen('mnlist:addrs')):
			old_mn_ips += [self.redis.lindex('mnlist:addrs', i).decode('utf-8')]

		for output, info_str in mn_list.items():
			if not info_str:
				continue

			info = info_str.split()
			#a += 1
			#if a > 3: break

			if len(info) < 7:
				print('Incomplete masternode info for: ' + output)
				mn_ips += [mn_ip]
				continue

			#if not output in mn_ranks:	# make sure there're no missing keys
			#	mn_ranks[output] = False
			mn_ip, mn_port = info[7].split(':')
			#mn_ip = '127.0.0.1'
			request_start = time.time()
			status = self.send_service_query(mn_ip + ':{{svc-port:system.net.tlsTunnel}}')
			request_end = time.time()
			mn = {
				'dapp_support': False,
				'protocol_version': info[1],
				'mn_version': '010200',	# default value for legacy MNnodes
				'payee': info[2],
				#'last_seen': info[3],
				#'active_seconds': info[4],
				#'last_paid_time': info[5],
				#'last_paid_block': info[6],
				#'last_rank': mn_ranks[output],
				'state_name': info[0],
				'last_checked_time': round(time.time()),
				'services': [],
				'output': output,
				'ip': mn_ip
			}

			# Check whether we've successfully received the JSON status message
			if status:
				# todo: try
				mn['dapp_support'] = True
				mn['services'] = list(status['services'].keys())
				mn['latency_ms'] = round((request_end - request_start) * 1000)	# todo: add default value above
				mn['api_version'] = status['blockchain']['api_version']
				mn['core_version'] = status['blockchain']['core_version']
				mn['mn_version'] = status['blockchain']['mn_version']
				dapp_support_ips += [mn_ip]

				if'services' in status:
					for service in status['services'].keys():
						if service not in self.lists['svc_providers']:
							self.lists['svc_providers'][service] = []

						if mn_ip not in self.lists['svc_providers'][service]:
                                                	self.lists['svc_providers'][service] += [mn_ip]

			self.lists['masternodes'][mn_ip] = mn
			mn_ips += [mn_ip]
			self.redis.set('mnlist:byaddr:' + mn_ip, json.dumps(mn))

			if mn_ip in old_mn_ips:
				old_mn_ips.remove(mn_ip)
				print('* %s' % mn_ip)
			else:
				self.on_mn_added_to_list(mn_ip)

			#return

		# Check what IPs are to be removed from the list
		for old_mn_ip in old_mn_ips:
			self.on_mn_removed_from_list(old_mn_ip)

		# Clear the old lists and save new ones
		for i in range(0, self.redis.llen('mnlist:addrs')):
			self.redis.lpop('mnlist:addrs')

		print(mn_ips)
		if (len(mn_ips)):
			self.redis.lpush('mnlist:addrs', *mn_ips)

		if (len(dapp_support_ips)):
			self.redis.lpush('mnlist:with:dapp_support', *dapp_support_ips)

		for service, providers in self.lists['svc_providers'].items():
			for i in range(0, self.redis.llen('svc_providers:' + service)):
				self.redis.lpop('svc_providers:' + service)

			self.redis.lpush('svc_providers:' + service, *providers)


	## Hooks
	def on_mn_added_to_list(self, mn_ip):
		print('+ ' + mn_ip)

	def on_mn_removed_from_list(self, mn_ip):
		print('- ' + mn_ip)

	## Tasks
	@asyncio.coroutine
	def service_discovery_task(self):
		print('Veles Masternode Service Discovery Daemon starting')
		while True:
			print('[ sleeping for %i s ]' % int(self.config('discovery_delay', 300)))
			yield from asyncio.sleep(int(self.config('discovery_delay', 300)))
			print('Starting full masternode service discovery ...')
			try:
				self.discover_all_services()
			except KeyboardInterrupt:
				print("\n* Shutting down on keyboard interrupt *")
				return
			except:
				print('An error has occured, retrying ...')
				continue


	def run_discovery_service(self):
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

	def run(self, arg = None):
		if arg == 'discover_all':
			self.discover_all_services()
		else:
			"Unknown command"

# Self-test, basic commandline interface
def main():
	if len(sys.argv) == 2 and sys.argv[1] == '--help':
		print("Veles MN Web Sync\nUsage: %s [config]\n" % sys.argv[0])
		return

	if len(sys.argv) > 1:
		server = VelesMNWebSync(sys.argv[1])
	else:
		server = VelesMNWebSync()
	if len(sys.argv) > 2:
		server.run(sys.argv[2])
	else:
		server.run()

if __name__=='__main__':
	main()


