""" Dummy mockup classes for testing and development """

class DummyVPNManagementGateway(object):
	def get_status(self):
		return {
			"client_count": 2,
			"client_list": [
				{
					"bytes_received": 5660970,
					"bytes_sent": 104576724,
					"client_id": "c9740ab311f1e2a260f46e373d69f1aa0b0852fea21959d5c565db94fd2d",
					"connected_since": "2019-12-06 17:38:48",
					"payment_status": "ALPHA_TRIAL",
					"session_id": "7e1d78cbc97cdde24e39bc37e193ff"
				},
				{
					"bytes_received": 576632553,
					"bytes_sent": 10163809726,
					"client_id": "caee60e7ca43642dc87734c81d7305686aabbe58008f6cf68067f6f83286",
					"connected_since": "2019-12-06 13:25:28",
					"payment_status": "ALPHA_TRIAL",
					"session_id": "941d9251e7c8516d5e2b9abce42632"
				}
			],
			"server_options": "[SSL (OpenSSL)] [LZO] [LZ4] [EPOLL] [PKCS11] [MH/PKTINFO] [AEAD]",
			"server_version": "2.4.4",
			"state_name": "CONNECTED",
			"up_since": "2019-12-03 15:40:13"
			}