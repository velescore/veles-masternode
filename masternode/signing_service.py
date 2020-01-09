""" Veles Masternode (gen 2) signing service """

class MasternodeSigningService(object):
	"""Service to manage signing and verification of MN communication"""

	def __init__(self, config, logger, core_node_service, mnsync_service):
		"""Constructor"""
		self.config = config
		self.logger = logger
		self.mnsync_service = mnsync_service
		self.core = core_node_service

	def sign(self, message):
		try:
			signature = self.core.call('signmessage', [
				self.config['masternode'].get('signing_key'),
				message
				])

		except Exception as e:
			signature = None
			self.logger.error('MasternodeSigningService::signmessage: Error: ' + str(e))

		return signature

	def verify(self, signature, message):
		try:
			signature = self.core.call('verifymessage', [
				self.config['masternode'].get('signing_key'),
				signature,
				message
				])

		except Exception as e:
			signature = None
			self.logger.error('MasternodeSigningService::signmessage: Error: ' + str(e))

		return signature
	