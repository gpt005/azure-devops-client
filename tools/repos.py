from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import requests
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

AZDO_RESOURCE = "499b84ac-1321-427f-aa17-267ca6975798/.default"


class RepoClient:
    def __init__(self, org: str, project: str, tenant_id: str | None = None):
        self.org = org
        self.project = project
        self._credential = AzureCliCredential(tenant_id=tenant_id) if tenant_id else AzureCliCredential()
        self.base = f"https://dev.azure.com/{org}/{requests.utils.quote(project, safe='')}"

    def _headers(self) -> dict[str, str]:
        token = self._credential.get_token(AZDO_RESOURCE).token
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{self.base}/_apis/{path}"
        r = requests.get(url, headers=self._headers(), params={"api-version": "7.1", **(params or {})}, timeout=30)
        r.raise_for_status()
        return r.json()

    def list_repos(self) -> list[dict]:
        return self._get("git/repositories").get("value", [])

    def get_repo(self, name_or_id: str) -> dict:
        repos = self.list_repos()
        match = next(
            (r for r in repos if r["name"].lower() == name_or_id.lower() or r["id"] == name_or_id),
            None,
        )
        if not match:
            names = [r["name"] for r in repos]
            print(f"Repo '{name_or_id}' not found. Available: {', '.join(names)}", file=sys.stderr)
            sys.exit(1)
        return match

    def browse(self, repo: str, path: str = "/", branch: str | None = None) -> list[dict]:
        r = self.get_repo(repo)
        params: dict = {"scopePath": path, "recursionLevel": "OneLevel"}
        if branch:
            params["versionDescriptor.version"] = branch
            params["versionDescriptor.versionType"] = "branch"
        return self._get(f"git/repositories/{r['id']}/items", params).get("value", [])

    def read_file(self, repo: str, path: str, branch: str | None = None) -> str:
        r = self.get_repo(repo)
        params: dict = {"path": path, "$format": "text"}
        if branch:
            params["versionDescriptor.version"] = branch
            params["versionDescriptor.versionType"] = "branch"
        url = f"{self.base}/_apis/git/repositories/{r['id']}/items"
        token = self._credential.get_token(AZDO_RESOURCE).token
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "text/plain"},
            params={"api-version": "7.1", **params},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.text

    def list_branches(self, repo: str) -> list[dict]:
        r = self.get_repo(repo)
        refs = self._get(f"git/repositories/{r['id']}/refs", {"filter": "heads/"}).get("value", [])
        return refs

    def list_commits(self, repo: str, branch: str | None = None, top: int = 20) -> list[dict]:
        r = self.get_repo(repo)
        params: dict = {"$top": top}
        if branch:
            params["searchCriteria.itemVersion.version"] = branch
            params["searchCriteria.itemVersion.versionType"] = "branch"
        return self._get(f"git/repositories/{r['id']}/commits", params).get("value", [])


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n}B"
    if n < 1024 ** 2:
        return f"{n // 1024}KB"
    return f"{n // 1024 ** 2}MB"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Azure DevOps Git repository browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  list                         List all repos in the project
  browse <repo> [--path /] [--branch <b>]   List files/dirs at a path
  read   <repo> <path> [--branch <b>]       Print file contents
  branches <repo>              List branches
  commits  <repo> [--branch <b>] [--top 20] Recent commits
""",
    )
    parser.add_argument("--org", default=os.environ.get("AZDO_ORG"))
    parser.add_argument("--project", default=os.environ.get("AZDO_PROJECT"))
    parser.add_argument("--tenant", default=os.environ.get("AZDO_TENANT"), help="Azure AD tenant ID (required for cross-tenant orgs)")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all repos")

    p_browse = sub.add_parser("browse", help="List files/dirs at a path")
    p_browse.add_argument("repo")
    p_browse.add_argument("--path", default="/")
    p_browse.add_argument("--branch")

    p_read = sub.add_parser("read", help="Print file contents")
    p_read.add_argument("repo")
    p_read.add_argument("path")
    p_read.add_argument("--branch")

    p_branches = sub.add_parser("branches", help="List branches")
    p_branches.add_argument("repo")

    p_commits = sub.add_parser("commits", help="List recent commits")
    p_commits.add_argument("repo")
    p_commits.add_argument("--branch")
    p_commits.add_argument("--top", type=int, default=20)

    args = parser.parse_args()

    if not args.org or not args.project:
        parser.error("Set AZDO_ORG and AZDO_PROJECT in .env or pass --org / --project.")

    client = RepoClient(org=args.org, project=args.project, tenant_id=getattr(args, "tenant", None))

    match args.command:
        case "list":
            repos = client.list_repos()
            print(f"{len(repos)} repo(s) in {args.org}/{args.project}:\n")
            for r in repos:
                default = " (default)" if r.get("isDisabled") is False and r.get("defaultBranch") else ""
                branch = r.get("defaultBranch", "").replace("refs/heads/", "")
                print(f"  {r['name']:<45} branch: {branch}")

        case "browse":
            items = client.browse(args.repo, path=args.path, branch=args.branch)
            label = f"{args.repo}{args.path}" + (f" @{args.branch}" if args.branch else "")
            print(f"{label}:\n")
            for item in items:
                kind = "DIR " if item.get("isFolder") else "FILE"
                size = f"  {_fmt_size(item.get('contentMetadata', {}).get('contentLength', 0))}" if kind == "FILE" else ""
                print(f"  {kind}  {item['path']}{size}")

        case "read":
            content = client.read_file(args.repo, args.path, branch=args.branch)
            print(content)

        case "branches":
            branches = client.list_branches(args.repo)
            print(f"{len(branches)} branch(es) in {args.repo}:\n")
            for b in branches:
                name = b["name"].replace("refs/heads/", "")
                print(f"  {name}")

        case "commits":
            commits = client.list_commits(args.repo, branch=args.branch, top=args.top)
            label = args.repo + (f" @{args.branch}" if args.branch else "")
            print(f"Recent commits in {label}:\n")
            for c in commits:
                sha = c["commitId"][:8]
                author = c.get("author", {}).get("name", "")
                date = c.get("author", {}).get("date", "")[:10]
                msg = c.get("comment", "").split("\n")[0][:72]
                print(f"  {sha}  {date}  {author:<25}  {msg}")

        case _:
            parser.print_help()
