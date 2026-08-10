from __future__ import annotations

import os
from typing import Any

import requests
from azure.identity import AzureCliCredential


AZURE_DEVOPS_RESOURCE_SCOPE = (
    "499b84ac-1321-427f-aa17-267ca6975798/.default"
)


class AzureDevOpsClient:
    def __init__(
        self,
        organization: str,
        project: str,
    ):
        self.organization = organization
        self.project = project
        self.credential = AzureCliCredential()
        self.base_url = (
            f"https://dev.azure.com/{self.organization}/{self.project}"
        )

    def _access_token(self) -> str:
        token = self.credential.get_token(AZURE_DEVOPS_RESOURCE_SCOPE)
        return token.token

    def _headers(self, content_type: str = "application/json") -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token()}",
            "Accept": "application/json",
            "Content-Type": content_type,
        }

    # -------------------------------------------------------------------------
    # Work Items — Read
    # -------------------------------------------------------------------------

    def get_work_item(self, work_item_id: int) -> dict[str, Any]:
        """Fetch a single work item by ID, including its relations."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}"
        response = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1", "$expand": "relations"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_work_items(self, ids: list[int], fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Fetch multiple work items by ID in a single request."""
        if not ids:
            return []
        default_fields = [
            "System.Id",
            "System.WorkItemType",
            "System.Title",
            "System.State",
            "System.AssignedTo",
            "System.IterationPath",
            "System.AreaPath",
            "System.Tags",
            "System.Description",
            "System.CreatedDate",
            "System.ChangedDate",
        ]
        url = f"{self.base_url}/_apis/wit/workitems"
        response = requests.get(
            url,
            headers=self._headers(),
            params={
                "api-version": "7.1",
                "ids": ",".join(str(i) for i in ids),
                "fields": ",".join(fields or default_fields),
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["value"]

    def query_work_items(self, wiql: str, top: int = 100) -> list[dict[str, Any]]:
        """Execute a WIQL query and return work items with fields populated."""
        query_url = f"{self.base_url}/_apis/wit/wiql"
        response = requests.post(
            query_url,
            headers=self._headers(),
            params={"api-version": "7.1", "$top": top},
            json={"query": wiql},
            timeout=30,
        )
        response.raise_for_status()
        results = response.json()
        ids = [item["id"] for item in results.get("workItems", [])]
        return self.get_work_items(ids)

    def my_open_items(self, top: int = 50) -> list[dict[str, Any]]:
        """Return all open work items assigned to the authenticated user."""
        return self.query_work_items(
            """
            SELECT [System.Id]
            FROM WorkItems
            WHERE
                [System.TeamProject] = @project
                AND [System.AssignedTo] = @Me
                AND [System.State] <> 'Closed'
            ORDER BY [System.ChangedDate] DESC
            """,
            top=top,
        )

    # -------------------------------------------------------------------------
    # Work Items — Write
    # -------------------------------------------------------------------------

    def update_work_item(
        self,
        work_item_id: int,
        operations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply a JSON Patch document to a work item."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}"
        response = requests.patch(
            url,
            headers=self._headers("application/json-patch+json"),
            params={"api-version": "7.1"},
            json=operations,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def set_field(self, work_item_id: int, field: str, value: Any) -> dict[str, Any]:
        """Set a single field on a work item."""
        return self.update_work_item(
            work_item_id,
            [{"op": "add", "path": f"/fields/{field}", "value": value}],
        )

    def set_state(self, work_item_id: int, state: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.State", state)

    def set_title(self, work_item_id: int, title: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.Title", title)

    def assign_to(self, work_item_id: int, email: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.AssignedTo", email)

    def set_tags(self, work_item_id: int, tags: list[str]) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.Tags", "; ".join(tags))

    def create_work_item(
        self,
        work_item_type: str,
        title: str,
        extra_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new work item of the given type (e.g. 'Task', 'Bug', 'User Story')."""
        url = (
            f"https://dev.azure.com/{self.organization}/{self.project}"
            f"/_apis/wit/workitems/${work_item_type}"
        )
        ops: list[dict[str, Any]] = [
            {"op": "add", "path": "/fields/System.Title", "value": title}
        ]
        for field, value in (extra_fields or {}).items():
            ops.append({"op": "add", "path": f"/fields/{field}", "value": value})
        response = requests.post(
            url,
            headers=self._headers("application/json-patch+json"),
            params={"api-version": "7.1"},
            json=ops,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    # -------------------------------------------------------------------------
    # Comments
    # -------------------------------------------------------------------------

    def add_comment(self, work_item_id: int, comment: str) -> dict[str, Any]:
        """Add a comment to a work item."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}/comments"
        response = requests.post(
            url,
            headers=self._headers(),
            params={"api-version": "7.1-preview.4"},
            json={"text": comment},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_comments(self, work_item_id: int) -> list[dict[str, Any]]:
        """Return all comments on a work item."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}/comments"
        response = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1-preview.4"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("comments", [])

    # -------------------------------------------------------------------------
    # Iterations / Sprints
    # -------------------------------------------------------------------------

    def get_iterations(self) -> list[dict[str, Any]]:
        """Return all iterations (sprints) for the project."""
        url = f"{self.base_url}/_apis/work/teamsettings/iterations"
        response = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("value", [])

    def get_current_iteration(self) -> dict[str, Any] | None:
        """Return the current (active) iteration, or None if not found."""
        url = f"{self.base_url}/_apis/work/teamsettings/iterations"
        response = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1", "$timeframe": "current"},
            timeout=30,
        )
        response.raise_for_status()
        values = response.json().get("value", [])
        return values[0] if values else None

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    def list_projects(self) -> list[dict[str, Any]]:
        """Return all projects in the organization."""
        url = f"https://dev.azure.com/{self.organization}/_apis/projects"
        response = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("value", [])


# -----------------------------------------------------------------------------
# CLI smoke-test / example usage
# -----------------------------------------------------------------------------

def _print_item(item: dict[str, Any]) -> None:
    f = item.get("fields", {})
    print(
        f"  [{item['id']}]"
        f"  {f.get('System.WorkItemType', '?'):12}"
        f"  {f.get('System.State', '?'):15}"
        f"  {f.get('System.Title', '')}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Azure DevOps CLI helper")
    parser.add_argument("--org", default=os.environ.get("AZDO_ORG"), required=not os.environ.get("AZDO_ORG"))
    parser.add_argument("--project", default=os.environ.get("AZDO_PROJECT"), required=not os.environ.get("AZDO_PROJECT"))
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("projects", help="List all projects in the organization")
    sub.add_parser("mine", help="List your open work items")

    p_get = sub.add_parser("get", help="Get a work item by ID")
    p_get.add_argument("id", type=int)

    p_state = sub.add_parser("state", help="Set work item state")
    p_state.add_argument("id", type=int)
    p_state.add_argument("state", help="e.g. Active, Closed, Resolved")

    p_comment = sub.add_parser("comment", help="Add a comment to a work item")
    p_comment.add_argument("id", type=int)
    p_comment.add_argument("text")

    p_create = sub.add_parser("create", help="Create a new work item")
    p_create.add_argument("type", help="Work item type, e.g. Task, Bug")
    p_create.add_argument("title")

    p_query = sub.add_parser("query", help="Run a WIQL query")
    p_query.add_argument("wiql", help="WIQL query string")
    p_query.add_argument("--top", type=int, default=50)

    sub.add_parser("sprint", help="Show current iteration / sprint")

    args = parser.parse_args()

    ado = AzureDevOpsClient(organization=args.org, project=args.project)

    match args.command:
        case "projects":
            for p in ado.list_projects():
                print(f"  {p['name']}")

        case "mine":
            items = ado.my_open_items()
            print(f"{len(items)} open item(s) assigned to you:\n")
            for item in items:
                _print_item(item)

        case "get":
            item = ado.get_work_item(args.id)
            f = item["fields"]
            print(f"ID:          {item['id']}")
            print(f"Type:        {f.get('System.WorkItemType')}")
            print(f"Title:       {f.get('System.Title')}")
            print(f"State:       {f.get('System.State')}")
            print(f"Assigned To: {f.get('System.AssignedTo', {}).get('displayName', 'Unassigned')}")
            print(f"Tags:        {f.get('System.Tags', '')}")
            print(f"Iteration:   {f.get('System.IterationPath')}")

        case "state":
            ado.set_state(args.id, args.state)
            print(f"Work item {args.id} state set to '{args.state}'.")

        case "comment":
            ado.add_comment(args.id, args.text)
            print(f"Comment added to work item {args.id}.")

        case "create":
            item = ado.create_work_item(args.type, args.title)
            print(f"Created {args.type} #{item['id']}: {args.title}")

        case "query":
            items = ado.query_work_items(args.wiql, top=args.top)
            print(f"{len(items)} result(s):\n")
            for item in items:
                _print_item(item)

        case "sprint":
            iteration = ado.get_current_iteration()
            if iteration:
                attrs = iteration.get("attributes", {})
                print(f"Name:  {iteration['name']}")
                print(f"Path:  {iteration['path']}")
                print(f"Start: {attrs.get('startDate', 'N/A')}")
                print(f"End:   {attrs.get('finishDate', 'N/A')}")
            else:
                print("No current iteration found.")

        case _:
            parser.print_help()
