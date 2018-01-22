import sys
import argparse
from os.path import join as path_join

from .storages import FolderStorage
from .renderers import JinjaRenderer, JinjaMarkdownContentRenderer
from .wikix import WikiX


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("path")

    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--host", default="127.0.0.1")

    dirs = parser.add_argument_group("dirs")
    dirs.add_argument("--pages", default="pages")
    dirs.add_argument("--static", default="static")
    dirs.add_argument("--templates", default="templates")

    parser.add_argument("--index-page", default="Welcome")

    args = parser.parse_args()

    pages_path = path_join(args.path, args.pages)
    static_path = path_join(args.path, args.static)
    templates_path = path_join(args.path, args.templates),
    r = JinjaRenderer(
        FolderStorage(pages_path, ".md"),
        FolderStorage(static_path),
        templates_path,
        lambda page_storage: JinjaMarkdownContentRenderer(
            page_storage, "__default"))
    WikiX(r, args.index_page, static_path).run(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
