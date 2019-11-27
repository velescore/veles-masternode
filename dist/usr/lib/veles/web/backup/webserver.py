#!/usr/bin/env python
import asyncio, sys, json, configparser
from aiohttp import web
import velesvpn, velescert, velesrpc

class VelesMNWebServer(object):
	headers_common = {"Server": "lighttpd/1.4.45"}
	headers_json = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
	headers_html = {"Content-Type": "text/html"}

	def __init__(self, config_path='/etc/veles/webserver.conf'):
		self.configparser = configparser.ConfigParser()
		self.configparser.read(config_path)
		self.services = { 'vpn': velesvpn.VelesVPNService() }

	def config(self, key, default = None, section = 'http_server'):
		try:
			return self.configparser[section].get(key, default)
		except:
			return None

	@asyncio.coroutine
	def handle_api(self, request):
		myarg = request.match_info.get('method', "status")
		text = ""
		headers = {}

		if myarg == 'getCertificate':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			result = {
				'certificate_data': cert
			}
			headers = self.headers_json
		elif myarg == 'getOpenVPNConfig':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(crt_service.make_openvpn_config(cert))
			headers = {
				"Content-Type": "application/openvpn",
				"Content-Disposition": "attachment; filename=veles.ovpn"
				}
		elif myarg == 'getOpenVPNShieldedConfig':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(crt_service.make_openvpn_shielded_config(cert))
			headers = {
				"Content-Type": "application/openvpn",
				"Content-Disposition": "attachment; filename=veles-shield.ovpn"
				}
		elif myarg == 'getStunnelConfig':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(crt_service.make_stunnel_config(cert))
			headers = {
				"Content-Type": "application/stunnel",
				"Content-Disposition": "attachment; filename=veles.stunnel.conf"
				}
		elif myarg == 'getStunnelCertificate':
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(cert['ca']) + "\n" + str(cert['certificate']) + "\n" + str(cert['key'])
			headers = {
				"Content-Type": "application/openssl",
				"Content-Disposition": "attachment; filename=stunnel.pem"
				}
		elif myarg == 'getCACertificate':	# todo: finish - don't generate all the shit just fetch ca file
			crt_service = velescert.VelesCertificateService()
			cert = crt_service.get_new_certificate()
			text = str(cert['ca'])
			headers = {
				"Content-Type": "application/openssl",
				"Content-Disposition": "attachment; filename=veles-ca.crt"
				}
		elif myarg == 'getAllConfigData':
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
				self.config('rpcport', '{{svc-port:system.wallet.velesCoreDaemon}}', 'veles_wallet'),
				self.config('rpcuser', None, 'veles_wallet'),
				self.config('rpcpassword', None, 'veles_wallet'),
				)
			chain_info = wallet.rpc_call('getblockchaininfo')
			net_info = wallet.rpc_call('getnetworkinfo')
			halving_info = wallet.rpc_call('gethalvingstatus')
			wallet_status = {
				'velesd_version': net_info['version'],
				'velesd_protocolversion': net_info['protocolversion'],
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

		handler = app.make_handler()
		task = asyncio.get_event_loop().create_server(
			handler,
			self.config('addr', '127.0.0.1'),
			self.config('port', {{svc-port:system.net.webServer}})
			)
		return task

	def run(self):
		loop = asyncio.get_event_loop()
		print("Running Veles Core WebServer at %s:%s" % (self.config('addr', '127.0.0.1'), str(self.config('port', {{svc-port:system.net.webServer}}))))
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


