#!/usr/bin/env python
import asyncio, sys, json
from aiohttp import web

class WebServer(object):
	headers_common = {"Server": "lighttpd/1.4.45"}
	headers_json = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
	headers_html = {"Content-Type": "text/html"}

	def __init__(self, controllers, config, logger):
		self.controllers = controllers
		self.config = config
		self.logger = logger

	def start_job(self):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(asyncio.gather(
			self.http_handler_task()
			))
		loop.run_forever()

	@asyncio.coroutine
	def http_handler_task(self):
		app = web.Application()

		self.logger.info('WebServer::http_handler_task: Starting asynchronous http_handler_task [%s:%s] ' % (self.conf('addr', '127.0.0.1'), str(self.conf('port', 21340))))
		app.router.add_get('/', self.handle_index)
		app.router.add_get('/api', self.controllers['StatusController']().handle)

		handler = app.make_handler()
		task = asyncio.get_event_loop().create_server(
			handler,
			self.conf('addr', '127.0.0.1'),
			self.conf('port', 21340)
			)
		return task

	@asyncio.coroutine
	def handle_index(self, request):
		#try:
		with open(self.conf('index_path', '/var/lib/veles/web/public/index.lighttpd.html'), 'r') as myfile:
			index = myfile.read()
		#except:
		#	index = "it works!"

		return web.Response(text=index, headers={**self.headers_common, **self.headers_html})

	def conf(self, key, default = None, section = 'webserver'):
		try:
			return self.config[section].get(key, default)
		except:
			return default



