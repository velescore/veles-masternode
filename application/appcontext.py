""" Main app entry point """

import logging, sys

class ApplicationContext(object):
	""" Minimalistic app entry point """

	def __init__(self, logger, jobs):
		self.logger = logger
		self.jobs = jobs

		# Set-up global logging
		logger.addHandler(logging.StreamHandler(sys.stdout))

	def init_dapps(self, container):
		container.dapp_registry().load_dapps(container)

	def run_job(self, job_name):
		""" Runs a job from jobs directory """
		if job_name in self.jobs.keys():
			self.jobs[job_name]().start_job()

		self.logger.error("Veles Masternode: No such job found: %s" % job_name)



