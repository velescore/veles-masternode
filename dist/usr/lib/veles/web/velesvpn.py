from openvpn_api import vpn
from hashlib import blake2b

class VelesVPNService(object):
	salt = ''

	def __init__(self, host = "127.0.0.1", port = 21432):
		self.host = host
		self.port = port
		self.openvpn = None

	def status(self):
		state = self.server().state
		status = self.server().get_status()
		rel = self.server().release
		h1 = blake2b(digest_size=15)
		h2 = blake2b(digest_size=30)
		result = {
			'client_list': [],
			'up_since': str(state.up_since),
			'state_name': state.state_name,
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
