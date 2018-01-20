#!/usr/bin/env python3
import os
import re
import sys
import argparse
import http.server
from os import path
from collections import defaultdict

import jinja2
import markdown
from tqdm import tqdm

CAT_RE = re.compile(r"<category>(.+)</category>")


def parse_cats(s):
    out = set()
    for i in reversed(list(CAT_RE.finditer(s))):
        out.add(i.group(1))
        s = s[:i.start()] + s[i.end():]
    return s, out


def load_func(args, macro_default):
    def inner(name):
        if not name:
            return None

        is_default = name == "__default"
        p = path.join(args.page_dir, name) + ".md"

        if not path.isfile(p):
            return None
        with open(p) as f:
            s = "" if is_default else macro_default
            s += f.read()
            return s, p, lambda: False
        return None
    return inner


def do_url_quote(s):
    return s.replace(" ", "_")


def build_url(label, base, end):
    return base + do_url_quote(label) + end


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("path")
    parser.add_argument("--no-progress-bar", action="store_true")

    build = parser.add_argument_group(title="build")
    build.add_argument("--index-page", default="Welcome")
    build.add_argument("--page-dir", "-p", default="pages")
    build.add_argument("--static-dir", "-s", default="static")
    build.add_argument("--meta-dir", "-m", default="meta")
    build.add_argument("--output-dir", "-o", default="output")

    server = parser.add_argument_group(title="server")
    server.add_argument("--server", action="store_true")
    server.add_argument("--address", default="")
    server.add_argument("--port", type=int, default=9999)

    args = parser.parse_args()

    os.chdir(args.path)

    if args.server:
        os.chdir(args.output_dir)

        Handler = http.server.SimpleHTTPRequestHandler
        httpd = http.server.HTTPServer((args.address, args.port), Handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            return
        return

    macro_default = path.join(args.page_dir, "__default.md")
    if path.isfile(macro_default):
        macro_default = '{% import "__default" as m %}\n'
    else:
        macro_default = "\n"

    env = jinja2.Environment(
        loader=jinja2.FunctionLoader(load_func(args, macro_default)),
        autoescape=False)
    meta_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(args.meta_dir),
        autoescape=False)
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.attr_list",
            "markdown.extensions.fenced_code",
            "markdown.extensions.footnotes",
            "markdown.extensions.tables",
            "markdown.extensions.toc",
            "markdown.extensions.wikilinks"],
        extension_configs={
            "markdown.extensions.wikilinks": {
                "build_url": build_url,
                "base_url": "/p/"}},
        output_format="html5")

    page_template = meta_env.get_template("page.html")
    page_index_template = meta_env.get_template("page-index.html")
    cat_template = meta_env.get_template("category.html")
    cat_index_template = meta_env.get_template("category-index.html")

    def tqdm_wrap(it):
        if args.no_progress_bar:
            yield from it
        else:
            yield from tqdm(it)

    def get_output_path(*paths):
        out = path.join(args.output_dir, *paths)
        os.makedirs(out, exist_ok=True)
        return out

    def write_template(p, template, **kwargs):
        os.makedirs(p, exist_ok=True)
        with open(path.join(p, "index.html"), "w") as f:
            f.write(template.render(**kwargs))

    def render_page(name, page, body, cats):
        output_path = get_output_path("p", page)
        kwargs = {
            "name": name,
            "body": body,
            "categories": sorted(cats)}

        write_template(output_path, page_template, **kwargs)

        if name != args.index_page:
            return
        write_template(get_output_path(), page_template, **kwargs)

    def render_cat(name, pages):
        output_path = get_output_path("c", name)
        pages = sorted(pages)
        kwargs = {
            "name": name,
            "pages": pages}

        write_template(output_path, cat_template, **kwargs)

    all_pages = set()
    all_cats = defaultdict(set)

    # /p/*.html
    for _, _, pages in tqdm_wrap(os.walk(args.page_dir)):
        for page in tqdm_wrap(pages):
            full_path = page
            page, _ = path.splitext(page)
            page = path.split(page)[1]

            page_body = env.get_template(page).render()
            page_body, cats = parse_cats(page_body)
            page_body = md.convert(page_body)

            if page in all_pages:
                parser.error("page '{}' is defined twice".format(page))
            all_pages.add(page)
            for cat in cats:
                all_cats[cat].add(page)

            name = page
            page = do_url_quote(page)
            render_page(name, page, page_body, cats)

    # /p/index.html
    write_template(get_output_path("p"), page_index_template, pages=sorted(all_pages))

    # /c/*/index.html
    for k, v in all_cats.items():
        render_cat(k, v)

    # /c/index.html
    write_template(get_output_path("c"), cat_index_template, categories=sorted(all_cats.keys()))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
