import re
import os.path
import mimetypes
from urllib.parse import quote as urlquote

import jinja2
import markdown

TAG_RE = re.compile(r"<tag>(.+?)</tag>")


def parse_tags(s):
    out = set()
    for i in reversed(list(TAG_RE.finditer(s))):
        out.add(i.group(1))
        s = s[:i.start()] + s[i.end():]
    return s, out


class JinjaMarkdownContentRenderer:
    def __init__(self, storage, macro_default_page, ext):
        self._storage = storage

        self._ext = ext
        self._macro_default_page = macro_default_page
        self._macro_import = '{{% import "{}" as m %}}\n'.format(macro_default_page)

        self._env = jinja2.Environment(
            loader=jinja2.FunctionLoader(self._load_jinja_template()),
            autoescape=False,
            cache_size=0)
        self._md = markdown.Markdown(
            extensions=[
                "markdown.extensions.attr_list",
                "markdown.extensions.fenced_code",
                "markdown.extensions.footnotes",
                "markdown.extensions.tables",
                "markdown.extensions.toc",
                "markdown.extensions.wikilinks"],
            extension_configs={
                "markdown.extensions.wikilinks": {
                    "build_url": self._build_url,
                    "base_url": "/p/",
                    "end_url": ""}},
            output_format="html5")

    def _load_jinja_template(self):
        def inner(name):
            if not name:
                return None

            macro_import = self._macro_import
            if not self._storage.exists(self._macro_default_page + self._ext):
                macro_import = "\n"
            is_default = name == self._macro_default_page

            out = "" if is_default else macro_import

            s = self._storage.content(name + self._ext)
            if s is None:
                return None
            return out + s
        return inner

    def _build_url(self, label, base, end):
        return base + urlquote(label) + end

    def __call__(self, name):
        if not self._storage.exists(name + self._ext):
            return None, None, None

        content = self._env.get_template(name).render()
        content, tags = parse_tags(content)
        raw_content = self._storage.content(name + self._ext)
        return raw_content, self._md.convert(content), tags


class JinjaRenderer:
    def __init__(self, page_storage, static_storage, template_path, content_renderer):
        self._page_storage = page_storage
        self._static_storage = static_storage

        self._content_renderer = content_renderer(self._page_storage)
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),  # TODO use a storage
            autoescape=False,
            cache_size=0)

    def page(self, name):
        # GET /p/{name}
        raw_content, content, tags = self._content_renderer(name)
        if raw_content is None:
            return None

        t = self._env.get_template("page.html")
        return t.render(
            name=name,
            content=content,
            raw_content=raw_content,
            tags=tags)

    def each_page(self):
        for page in self._page_storage.each():
            raw_content, content, tags = self._content_renderer(page)
            if raw_content is None:
                continue
            yield page, raw_content, content, tags

    def page_all(self):
        # GET /p
        pages = set()
        for i in self._page_storage.each():
            pages.add(i)

        t = self._env.get_template("page-all.html")
        return t.render(
            pages=pages)

    def tag(self, tag):
        # GET /t/{tag}
        pages = set()
        for page, _, _, tags in self.each_page():
            if tag in tags:
                pages.add(page)

        t = self._env.get_template("tag.html")
        return t.render(
            name=tag,
            pages=pages)

    def tag_all(self):
        # GET /t
        tags = set()
        for _, _, _, new_tags in self.each_page():
            tags.update(new_tags)

        t = self._env.get_template("tag-all.html")
        return t.render(
            tags=tags)

    def search(self, pages):
        t = self._env.get_template("search.html")
        return t.render(
            pages=pages)

    def static(self, name):
        return self._static_storage.content(name, True), mimetypes.guess_type(name, False)[0]

    def static_all(self):
        statics = set()
        for i in self._static_storage.each():
            statics.add(i)

        t = self._env.get_template("static-all.html")
        return t.render(
            statics=statics)
