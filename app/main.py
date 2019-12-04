""" Main methods that get called by CLI. This is (hopefully)
    the only non-OOP Python file in the project """

def run_job(jobs, job_name):
	if job_name in jobs:
		try:
			return jobs[job_name]().start_job()
		except KeyboardInterrupt:
			print("\nVelesMasternodeCLI: Shutting down on keyboard interrupt\n")
			return
		except:
			raise ValueError("Failed to run job: %s" % job_name)
	raise ValueError("Failed to find job: %s" % job_name)

