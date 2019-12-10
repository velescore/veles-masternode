""" Veles Masternode (gen 2) masternode module base classes """
from abc import ABCMeta, abstractmethod
import copy

class AbstractFillableObject(object, metaclass=ABCMeta):
	""" Object that can be easily fileld with attributes at creation """
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
				setattr(self, name, copy.copy(value))

	def attributes(self):
		attributes = {}

		# Put properties in dict, skip 'private' ones
		for attr_name, attr_value in self.__dict__.items():
			if attr_name[0] != '_':
				attributes[attr_name] = attr_value

		return attributes

class AbstractFillableCollection(dict, metaclass=ABCMeta):
	""" Represents a dictionary of AbstractFillableObject instances """
	def __init__(self, entries):
		self.fill(entries)

	def __setitem__(self, key, value):
		#assert issubclass(value, AbstractFillableObject)
		dict.__setitem__(self, key, value)

	def fill(self, entries):
		for key, value in entries.items():
			self[key] = value

	def attributes(self):
		attributes = {}

		# Get attributes of each item
		for attr_name, attr_value in self.items():
			if attr_name[0] != '_':
				attributes[attr_name] = attr_value.attributes()

		return attributes

