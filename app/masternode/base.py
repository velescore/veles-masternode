""" Veles Masternode (gen 2) masternode module base classes """

class BaseFillableObject(object):
	_required = []

	def __init__(self, attributes):
		self.fill(attributes)

	def fill(self, attributes):
		# Fill required attributes
		for req_attr in self._required:
			if req_attr not in attributes:
				raise ValueError('BaseFillableObject::fill: required atribute %s not given' % req_attr)
			setattr(self, req_attr, attributes[req_attr])

		# Fill optional attributes (need to be declared with default value)
		for name, value in attributes.items():
			if hasattr(self, name):
				setattr(self, name, value)

	def attributes(self):
		return self.__dict__
