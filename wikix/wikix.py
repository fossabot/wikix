from asyncio import coroutine
from urllib.parse import unquote as urlunquote

from aiohttp import web

from .storages import FolderStorage
from .renderers import JinjaRenderer, JinjaMarkdownContentRenderer


class WikiX:
    def __init__(self, renderer, index_page, static_path=None):
        self._renderer = renderer

        self._index_page = index_page
        self._static_path = static_path

        self._app = web.Application()
        self._add_routes()

    def _add_routes(self):
        self._app.router.add_get("/", self.get_index)

        self._app.router.add_get("/p", self.get_page_all)
        self._app.router.add_get("/p/{name}", self.get_page)

        self._app.router.add_get("/t", self.get_tag_all)
        self._app.router.add_get("/t/{tag}", self.get_tag)

        self._app.router.add_get("/s", self.get_static_all)
        if self._static_path is None:
            self._app.router.add_get("/s/{static}", self.get_static)
        else:
            self._app.router.add_static("/s", self._static_path)

    @coroutine
    def get_index(self, req):
        return web.Response(
            body=self._renderer.page(self._index_page),
            content_type="text/html")

    @coroutine
    def get_page_all(self, req):
        return web.Response(
            body=self._renderer.page_all(),
            content_type="text/html")

    @coroutine
    def get_page(self, req):
        name = req.match_info.get("name", None)
        if name is None:
            raise web.HTTPNotFound()

        name = urlunquote(name)
        data = self._renderer.page(name)
        if not data:
            raise web.HTTPNotFound()

        return web.Response(body=data, content_type="text/html")

    @coroutine
    def get_tag_all(self, req):
        return web.Response(
            body=self._renderer.tag_all(),
            content_type="text/html")

    @coroutine
    def get_tag(self, req):
        tag = req.match_info.get("tag", None)
        if tag is None:
            raise web.HTTPNotFound()

        tag = urlunquote(tag)
        data = self._renderer.tag(tag)
        if not data:
            raise web.HTTPNotFound()

        return web.Response(body=data, content_type="text/html")

    @coroutine
    def get_static_all(self, req):
        return web.Response(
            body=self._renderer.static_all(),
            content_type="text/html")

    @coroutine
    def get_static(self, req):
        name = req.match_info.get("static", None)
        if name is None:
            raise web.HTTPNotFound()

        data, content_type = self._renderer.static(name)
        if not data:
            raise web.HTTPNotFound()
        if content_type is None:
            content_type = "application/octet-stream"

        return web.Response(body=data, content_type=content_type)

    def run(self, host, port):
        web.run_app(self._app, host=host, port=port)
