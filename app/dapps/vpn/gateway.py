from openvpn_api import vpn
from hashlib import blake2b

class VPNManagementGateway(object):
	salt = ''

	def __init__(self, config, logger):
		self.host = config['dapps.vpn'].get('host', '127.0.0.1')
		self.port = config['dapps.vpn'].get('port', '21432')
		self.config = config
		self.logger = logger
		self.openvpn = None

	def get_status(self):
		state = self.server().state
		status = self.server().get_status()
		rel = self.server().release
		h1 = blake2b(digest_size=15)
		h2 = blake2b(digest_size=30)
		result = {
			'client_list': [],
			'up_since': str(state.up_since),
			'server_state': state.state_name,
			'client_count': len(status.client_list),
			'server_options': rel[rel.find('['):rel.rfind(']')+1],
			'server_version': self.server().version
			}

		for addr, client in status.client_list.items():
			h1.update(addr.encode('utf-8'))
			h2.update(client.common_name.encode('utf-8'))

			result['client_list'] += [{
				'session_id': h1.hexdigest(),
				'client_id': h2.hexdigest(),
				'bytes_received': int(client.bytes_received),
				'bytes_sent': int(client.bytes_sent),
				'connected_since': str(client.connected_since),
				'payment_status': 'ALPHA_TRIAL'
				}]

		return result

	def server(self):
		if not self.openvpn:
			self.openvpn = vpn.VPN(self.host, self.port)
			self.openvpn.connect()

		return self.openvpn
