from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
from ado_client import AzureDevOpsClient

load_dotenv()


def _print_pages(node: dict[str, Any], indent: int = 0) -> None:
    path = node.get("path", "")
    print("  " + "  " * indent + (path or "/"))
    for sub in node.get("subPages", []):
        _print_pages(sub, indent + 1)


def _resolve_path(path: str) -> str:
    """Normalize a wiki page path to the form the API expects.

    ADO wiki markdown links use hyphens for spaces and %2D for real hyphens,
    e.g. /Migration-and-Self%2Dservice/Start-Here.  When the path contains
    percent-encoding, decode it using that convention so the caller can
    paste a link from a wiki page directly.  Plain paths (with spaces or *)
    are returned unchanged.
    """
    if "%" not in path:
        return path
    # Protect real hyphens encoded as %2D / %2d before any other decode.
    placeholder = "\x00"
    normalized = path.replace("%2D", placeholder).replace("%2d", placeholder)
    normalized = urllib.parse.unquote(normalized)
    normalized = normalized.replace("-", " ")
    return normalized.replace(placeholder, "-")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Azure DevOps wiki CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  list               List all wikis in the project
  pages              Browse the page tree (--wiki, --path, --depth)
  read <path>        Print a page's markdown content (--wiki)
  write <path> <file>  Create or update a wiki page from a markdown file
""",
    )
    parser.add_argument("--org", default=os.environ.get("AZDO_ORG"))
    parser.add_argument("--project", default=os.environ.get("AZDO_PROJECT"))
    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="List all wikis in the project")

    # pages
    p_pages = sub.add_parser("pages", help="Browse the page tree")
    p_pages.add_argument("--wiki", dest="wiki_id", help="Wiki identifier (default: first wiki)")
    p_pages.add_argument("--path", default="/", help="Root path (default: /)")
    p_pages.add_argument("--depth", type=int, default=3, help="Tree depth (default: 3)")

    # read
    p_read = sub.add_parser("read", help="Read a wiki page")
    p_read.add_argument("path", help="Page path, e.g. /Contracts/01-Auth")
    p_read.add_argument("--wiki", dest="wiki_id", help="Wiki identifier (default: first wiki)")

    # write
    p_write = sub.add_parser("write", help="Create or update a wiki page from a markdown file")
    p_write.add_argument("path", help="Page path, e.g. /Standards & Process/Boards Governance")
    p_write.add_argument("file", help="Path to the local markdown file to upload")
    p_write.add_argument("--wiki", dest="wiki_id", help="Wiki identifier (default: first wiki)")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a wiki page and all its sub-pages")
    p_delete.add_argument("path", help="Page path to delete")
    p_delete.add_argument("--wiki", dest="wiki_id", help="Wiki identifier (default: first wiki)")

    args = parser.parse_args()

    if not args.org or not args.project:
        parser.error(
            "Set AZDO_ORG and AZDO_PROJECT in your .env file or pass --org / --project."
        )

    ado = AzureDevOpsClient(organization=args.org, project=args.project)
    wikis = ado.list_wikis()
    default_wiki = wikis[0]["id"] if wikis else None

    match args.command:
        case "list":
            print(f"{len(wikis)} wiki(s):\n")
            for w in wikis:
                print(f"  {w['id']:40}  {w.get('name', '')}  ({w.get('type', '')})")

        case "pages":
            wiki_id = getattr(args, "wiki_id", None) or default_wiki
            if not wiki_id:
                print("No wikis found.")
            else:
                tree = ado.list_wiki_pages(wiki_id, path=args.path, depth=args.depth)
                print(f"Pages in '{wiki_id}' (path={args.path}, depth={args.depth}):\n")
                _print_pages(tree)

        case "read":
            wiki_id = getattr(args, "wiki_id", None) or default_wiki
            if not wiki_id:
                print("No wikis found.")
            else:
                resolved = _resolve_path(args.path)
                page = ado.get_wiki_page(wiki_id, resolved)
                print(f"# {page.get('path', resolved)}\n")
                print(page.get("content", "(no content)"))

        case "write":
            wiki_id = getattr(args, "wiki_id", None) or default_wiki
            if not wiki_id:
                print("No wikis found.")
            else:
                with open(args.file, "r", encoding="utf-8") as f:
                    content = f.read()
                resolved = _resolve_path(args.path)
                result = ado.upsert_wiki_page(wiki_id, resolved, content)
                url = result.get("remoteUrl") or result.get("url", "")
                print(f"Page written: {resolved}")
                if url:
                    print(f"URL: {url}")

        case "delete":
            wiki_id = getattr(args, "wiki_id", None) or default_wiki
            if not wiki_id:
                print("No wikis found.")
            else:
                resolved = _resolve_path(args.path)
                ado.delete_wiki_page(wiki_id, resolved)
                print(f"Deleted: {resolved}")

        case _:
            parser.print_help()
