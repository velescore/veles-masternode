#!/usr/bin/env python3
import sys, asyncio
from mnsync import VelesMNWebSync

def main():
	if len(sys.argv) == 2 and sys.argv[1] == '--help':
		print("Veles MN Web Sync\nUsage: %s [config]\n" % sys.argv[0])
		return

	if len(sys.argv) > 1:
		server = VelesMNWebSync(sys.argv[1])
	else:
		server = VelesMNWebSync()

	server.run_discovery_service()

if __name__=='__main__':
	main()


