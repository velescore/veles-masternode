#!/usr/bin/env python
import asyncio, sys, json, configparser, redis
from aiohttp import web
import velesvpn, velescert, velesrpc

class VelesMNWebServer(object):
	headers_common = {"Server": "lighttpd/1.4.45"}
	headers_json = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
	headers_html = {"Content-Type": "text/html"}
	api_version = '000099'
	mn_version = '010099'

	def __init__(self, config_path='/etc/veles/webserver.conf'):
		self.configparser = configparser.ConfigParser()
		self.configparser.read(config_path)
		self.services = { 'vpn': velesvpn.VelesVPNService() }
		self.redis = redis.Redis(
			host=self.config('host', '127.0.0.1', 'redis_db'),
			port=int(self.config('port', '21345', 'redis_db')),
			db=self.config('db', '0', 'redis_db')
		)
		# Add own Masternode IP to the header, for use with proxies etc.
		self.headers_common.update({"X-Veles-Masternode-IP": self.config('server_addr')})

	def config(self, key, default = None, section = 'http_server'):
		try:
			return self.configparser[section].get(key, default)
		except:
			return default

	@asyncio.coroutine
	def handle_api(self, request):
		method = request.match_info.get('method', "status")
		text = ""
		headers = {}

		if method == 'getCertificate':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			result = {
				'certificate_data': cert
			}
			headers = self.headers_json
		elif method == 'getOpenVPNConfig':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(crt_service.make_openvpn_config(cert))
			headers = {
				"Content-Type": "application/x-openvpn-profile",
				"Content-Disposition": "attachment; filename=veles.ovpn"
				}
		elif method == 'getOpenVPNShieldedConfig':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(crt_service.make_openvpn_shielded_config(cert))
			headers = {
				"Content-Type": "application/openvpn",
				"Content-Disposition": "attachment; filename=veles-shield.ovpn"
				}
		elif method == 'getStunnelConfig':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(crt_service.make_stunnel_config(cert))
			headers = {
				"Content-Type": "application/stunnel",
				"Content-Disposition": "attachment; filename=veles.stunnel.conf"
				}
		elif method == 'getStunnelCertificate':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(cert['ca']) + "\n" + str(cert['certificate']) + "\n" + str(cert['key'])
			headers = {
				"Content-Type": "application/openssl",
				"Content-Disposition": "attachment; filename=stunnel.pem"
				}
		elif method == 'getCACertificate':	# todo: finish - don't generate all the shit just fetch ca file
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(cert['ca'])
			headers = {
				"Content-Type": "application/openssl",
				"Content-Disposition": "attachment; filename=veles-ca.crt"
				}
		elif method == 'getAllConfigData':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			result = {
				'certificate_data': cert,
				'openvpn_config': crt_service.make_openvpn_config(cert),
				'stunnel_config': crt_service.make_stunnel_config(cert)
			}
			headers = self.headers_json
		else:
			try:
				vpn_status = self.services['vpn'].status()
			except:
				vpn_status = None

			#try:
			wallet = velesrpc.VelesRPCClient(
				self.config('rpchost', '127.0.0.1', 'veles_wallet'),
				self.config('rpcport', '21337', 'veles_wallet'),
				self.config('rpcuser', None, 'veles_wallet'),
				self.config('rpcpassword', None, 'veles_wallet'),
				)
			chain_info = wallet.rpc_call('getblockchaininfo')
			net_info = wallet.rpc_call('getnetworkinfo')
			halving_info = wallet.rpc_call('gethalvingstatus')
			wallet_status = {
				'core_version': net_info['version'],
				'protocol_version': net_info['protocolversion'],
				'mn_version': self.mn_version,
				'api_version': self.api_version,
				'blocks': chain_info['blocks'],
				'bestblockhash': chain_info['bestblockhash'],
				'difficulty': chain_info['difficulty'],
				'timeoffset': net_info['timeoffset'],
				'connections': net_info['connections'],
				'relayfee': net_info['connections'],
				'halvings_occured': halving_info['halvings_occured'],
				'blocks_to_next_epoch': halving_info['blocks_to_next_epoch'],
				'epoch_supply_target_reached': halving_info['epoch_supply_target_reached'],
			}
			mn_status = wallet.rpc_call('masternode', ['status'])
			try:
				mn_status['state_name'] = wallet.rpc_call('masternodelist', ['status', mn_status['outpoint']])[mn_status['outpoint']]
			except:
				mn_status['state_name'] = 'UNKNOWN'
			#except:
			#	wallet_status = None
			#	mn_status = None

			result = {
				'blockchain': wallet_status,
				'masternode': mn_status,
				'services': {'vpn': self.services['vpn'].status()}
			}

		if text == "":
			headers = self.headers_json
			text = json.dumps({
				'status': 'success',
				'method': 'status',
				'result': result
				}, sort_keys = True, indent = 4)

		return web.Response(text=text, headers={**self.headers_common, **headers})

	@asyncio.coroutine
	def handle_mn_api(self, request):
		method = request.match_info.get('method', "full")
		filter = request.match_info.get('filter', "all")
		text = ""
		headers = {}

		if method == 'list':
			result = {}
			#try:
			wallet = velesrpc.VelesRPCClient(
				self.config('rpchost', '127.0.0.1', 'veles_wallet'),
				self.config('rpcport', '21337', 'veles_wallet'),
				self.config('rpcuser', None, 'veles_wallet'),
				self.config('rpcpassword', None, 'veles_wallet'),
			)
			mn_list = wallet.rpc_call('masternodelist', ['full'])

			# Merge current mnlist from daemon with extended data in redis
			for i in range(0, self.redis.llen('mnlist:addrs')):
				try:
					mn_ip = self.redis.lindex('mnlist:addrs', i).decode('utf-8')
					mn_info = json.loads(self.redis.get('mnlist:byaddr:' + mn_ip).decode('utf-8'))
					core_info = mn_list[mn_info['output']].split()
				except:
					continue

				if filter == 'dapp_support' and mn_info['dapp_support'] == False:
					continue

				mn_info.update({
					'state_name': core_info[0],
					'last_seen': core_info[3],
					'activeseconds': core_info[4],
					'last_paid_time': core_info[5],
					'last_paid_block': core_info[6],
				})
				result[mn_ip] = mn_info

			headers = self.headers_json

		else:
                        text = json.dumps({
                                'status': 'error',
                                'method': method,
                                'result': 'Unknown method: %s' % method
                                }, sort_keys = True, indent = 4)

		if text == "":
			headers = self.headers_json
			text = json.dumps({
				'status': 'success',
				'method': 'status',
				'result': result
				}, sort_keys = True, indent = 4)

		return web.Response(text=text, headers={**self.headers_common, **headers})

	@asyncio.coroutine
	def handle_index(self, request):
		try:
			with open(self.config('index_path', '/var/lib/veles/web/public/index.lighttpd.html'), 'r') as myfile:
				index = myfile.read()
		except:
			index = "it works!"

		return web.Response(text=index, headers={**self.headers_common, **self.headers_html})


	@asyncio.coroutine
	def http_handler_task(self):
		app = web.Application()
		app.router.add_get('/', self.handle_index)
		app.router.add_get('/api/{method}', self.handle_api)
		app.router.add_get('/api/mn/{method}', self.handle_mn_api)
		app.router.add_get('/api/mn/{method}/{filter}', self.handle_mn_api)

		handler = app.make_handler()
		task = asyncio.get_event_loop().create_server(
			handler,
			self.config('addr', '127.0.0.1'),
			self.config('port', 21340)
			)
		return task

	def run(self):
		loop = asyncio.get_event_loop()
		print("Running Veles Core WebServer at %s:%s" % (self.config('addr', '127.0.0.1'), str(self.config('port', 21340))))
		#try:
		loop.run_until_complete(asyncio.gather(
			self.http_handler_task()
			))
		loop.run_forever()
		#except KeyboardInterrupt:
		#	print("\n* Shutting down on keyboard interrupt *")
		#except:
		#	print("\n* Shutting down on error")

# Self-test, basic commandline interface
def main():
	if len(sys.argv) == 2 and sys.argv[1] == '--help':
		print("VelesMN httpd server\nUsage: %s [config]\n" % sys.argv[0])
		return

	if len(sys.argv) > 1:
		server = VelesMNWebServer(sys.argv[1])
	else:
		server = VelesMNWebServer()

	server.run()

if __name__=='__main__':
	main()


