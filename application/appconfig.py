""" Wapper for configparser """

import os
from configparser import ConfigParser

class ApplicationConfig(ConfigParser):
	default_section='DEFAULT'

	""" Interface for using configuration,  """
	def __init__(self, filename):
		super().__init__(self)

		if not os.path.isfile(filename):
			raise ValueException('Configuration file not found: ' + filename)

		try:
			self.read(filename)
		except:
			raise ValueException('Error reading configuration file: ' + filename)


