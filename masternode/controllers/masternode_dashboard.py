#!/usr/bin/env python
from aiohttp import web
from .interfaces import AbstractController

class MasternodeDashboardController(AbstractController):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        # Use the inherited 'conf' method to retrieve the path for static files
        self.static_files_dir = self.conf('index_path', '/var/lib/veles/web/mndash/public', section='dashboard')

    def set_routes(self, router):
        # Serve files from the 'static_files_dir' under the '/mndash/' path
        router.add_static('/mndash/', path=self.static_files_dir, name='mndash')

        # Redirect to '/mndash/index.html' for the root or just '/mndash/'
        router.add_get('', self.redirect_to_index)
        router.add_get('/', self.redirect_to_index)

        # Catch-all handler for any other requests
        router.add_route('*', '/{tail:.*}', self.handle)

    async def redirect_to_index(self, request):
        # Redirect to the index.html file within the static files directory
        raise web.HTTPFound('/mndash/index.html')

    async def handle(self, request):
        # Fallback handler for requests not caught by static or specific routes
        return web.Response(text="This route is not handled.", status=404)
