""" Memory repository for debugging purposes """

class MasternodeRepository(object):
	""" Does CRUD operation with Masternode object on dummy database """
	data = {}

	def store(self, model):
		self.data[model.ip] = model

	def get(self, key):
		if key in self.data:
			return self.data[key]

		return None

	def get_all(self):
		return self.data

	def get_keys(self):
		return self.data.keys()

	def exists(self, key):
		return key in self.data

	def delete(self, key):
		self.data.pop(key)

 		