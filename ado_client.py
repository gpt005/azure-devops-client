from __future__ import annotations

from typing import Any

import requests
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()


AZURE_DEVOPS_RESOURCE_SCOPE = "499b84ac-1321-427f-aa17-267ca6975798/.default"

DEFAULT_FIELDS = [
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
    "System.CreatedBy",
]


class AzureDevOpsClient:
    def __init__(self, organization: str, project: str):
        self.organization = organization
        self.project = project
        self.credential = AzureCliCredential()
        self.base_url = f"https://dev.azure.com/{self.organization}/{self.project}"
        self.org_url = f"https://dev.azure.com/{self.organization}"

    def _access_token(self) -> str:
        return self.credential.get_token(AZURE_DEVOPS_RESOURCE_SCOPE).token

    def _headers(self, content_type: str = "application/json") -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token()}",
            "Accept": "application/json",
            "Content-Type": content_type,
        }

    # -------------------------------------------------------------------------
    # Work Items — List / Read
    # -------------------------------------------------------------------------

    def get_work_item(self, work_item_id: int) -> dict[str, Any]:
        """Fetch a single work item by ID, including relations."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}"
        r = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1", "$expand": "relations"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_work_items(
        self, ids: list[int], fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Fetch multiple work items by ID in a single request."""
        if not ids:
            return []
        url = f"{self.base_url}/_apis/wit/workitems"
        r = requests.get(
            url,
            headers=self._headers(),
            params={
                "api-version": "7.1",
                "ids": ",".join(str(i) for i in ids),
                "fields": ",".join(fields or DEFAULT_FIELDS),
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["value"]

    def query_work_items(self, wiql: str, top: int = 100) -> list[dict[str, Any]]:
        """Execute a WIQL query and return work items with fields populated."""
        r = requests.post(
            f"{self.base_url}/_apis/wit/wiql",
            headers=self._headers(),
            params={"api-version": "7.1", "$top": top},
            json={"query": wiql},
            timeout=30,
        )
        r.raise_for_status()
        ids = [item["id"] for item in r.json().get("workItems", [])]
        return self.get_work_items(ids)

    def list_work_items(
        self,
        work_item_type: str | None = None,
        state: str | None = None,
        assigned_to: str | None = None,
        tags: list[str] | None = None,
        area_path: str | None = None,
        iteration_path: str | None = None,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        """List work items with optional filters. All filters are ANDed together."""
        conditions = ["[System.TeamProject] = @project"]
        if work_item_type:
            conditions.append(f"[System.WorkItemType] = '{work_item_type}'")
        if state:
            conditions.append(f"[System.State] = '{state}'")
        if assigned_to:
            value = "@Me" if assigned_to.lower() in ("@me", "me") else f"'{assigned_to}'"
            conditions.append(f"[System.AssignedTo] = {value}")
        if tags:
            for tag in tags:
                conditions.append(f"[System.Tags] CONTAINS '{tag}'")
        if area_path:
            conditions.append(f"[System.AreaPath] UNDER '{area_path}'")
        if iteration_path:
            conditions.append(f"[System.IterationPath] UNDER '{iteration_path}'")
        wiql = (
            "SELECT [System.Id] FROM WorkItems WHERE "
            + " AND ".join(conditions)
            + " ORDER BY [System.ChangedDate] DESC"
        )
        return self.query_work_items(wiql, top=top)

    def my_open_items(self, top: int = 50) -> list[dict[str, Any]]:
        """Return all open work items assigned to the authenticated user."""
        return self.list_work_items(assigned_to="@me", top=top)

    def list_by_sprint(
        self, iteration_path: str | None = None, top: int = 50
    ) -> list[dict[str, Any]]:
        """List work items in a sprint. Uses current sprint if iteration_path is omitted."""
        if iteration_path:
            return self.list_work_items(iteration_path=iteration_path, top=top)
        sprint = self.get_current_iteration()
        if not sprint:
            return []
        return self.list_work_items(iteration_path=sprint["path"], top=top)

    # -------------------------------------------------------------------------
    # Work Items — Create
    # -------------------------------------------------------------------------

    def create_work_item(
        self,
        work_item_type: str,
        title: str,
        description: str | None = None,
        assigned_to: str | None = None,
        tags: list[str] | None = None,
        area_path: str | None = None,
        iteration_path: str | None = None,
        extra_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new work item (Task, Bug, User Story, Feature, Epic, etc.)."""
        url = f"{self.base_url}/_apis/wit/workitems/${work_item_type}"
        ops: list[dict[str, Any]] = [
            {"op": "add", "path": "/fields/System.Title", "value": title}
        ]
        if description:
            ops.append({"op": "add", "path": "/fields/System.Description", "value": description})
        if assigned_to:
            ops.append({"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to})
        if tags:
            ops.append({"op": "add", "path": "/fields/System.Tags", "value": "; ".join(tags)})
        if area_path:
            ops.append({"op": "add", "path": "/fields/System.AreaPath", "value": area_path})
        if iteration_path:
            ops.append({"op": "add", "path": "/fields/System.IterationPath", "value": iteration_path})
        for field, value in (extra_fields or {}).items():
            ops.append({"op": "add", "path": f"/fields/{field}", "value": value})
        r = requests.post(
            url,
            headers=self._headers("application/json-patch+json"),
            params={"api-version": "7.1"},
            json=ops,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    # -------------------------------------------------------------------------
    # Work Items — Update
    # -------------------------------------------------------------------------

    def update_work_item(
        self, work_item_id: int, operations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Apply a JSON Patch document to a work item."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}"
        r = requests.patch(
            url,
            headers=self._headers("application/json-patch+json"),
            params={"api-version": "7.1"},
            json=operations,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def set_field(self, work_item_id: int, field: str, value: Any) -> dict[str, Any]:
        return self.update_work_item(
            work_item_id,
            [{"op": "add", "path": f"/fields/{field}", "value": value}],
        )

    def set_title(self, work_item_id: int, title: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.Title", title)

    def set_description(self, work_item_id: int, description: str) -> dict[str, Any]:
        """Set (or replace) the description of a work item. Accepts plain text or HTML."""
        return self.set_field(work_item_id, "System.Description", description)

    def set_state(self, work_item_id: int, state: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.State", state)

    def assign_to(self, work_item_id: int, email: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.AssignedTo", email)

    def set_tags(self, work_item_id: int, tags: list[str]) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.Tags", "; ".join(tags))

    def set_area(self, work_item_id: int, area_path: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.AreaPath", area_path)

    def set_iteration(self, work_item_id: int, iteration_path: str) -> dict[str, Any]:
        return self.set_field(work_item_id, "System.IterationPath", iteration_path)

    # -------------------------------------------------------------------------
    # Work Items — Delete
    # -------------------------------------------------------------------------

    def delete_work_item(self, work_item_id: int, destroy: bool = False) -> None:
        """
        Delete a work item. By default it is soft-deleted (moves to recycle bin).
        Pass destroy=True for permanent deletion (irreversible).
        """
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}"
        r = requests.delete(
            url,
            headers=self._headers(),
            params={"api-version": "7.1", "destroy": str(destroy).lower()},
            timeout=30,
        )
        r.raise_for_status()

    def restore_work_item(self, work_item_id: int) -> dict[str, Any]:
        """Restore a soft-deleted work item from the recycle bin."""
        url = f"{self.base_url}/_apis/wit/recyclebin/{work_item_id}"
        r = requests.patch(
            url,
            headers=self._headers("application/json-patch+json"),
            params={"api-version": "7.1"},
            json=[{"op": "replace", "path": "/isDeleted", "value": "false"}],
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    # -------------------------------------------------------------------------
    # Comments — CRUD
    # -------------------------------------------------------------------------

    def get_comments(self, work_item_id: int) -> list[dict[str, Any]]:
        """Return all comments on a work item, newest first."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}/comments"
        r = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1-preview.4", "$orderBy": "createdDate desc"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("comments", [])

    def add_comment(self, work_item_id: int, text: str) -> dict[str, Any]:
        """Add a comment to a work item."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}/comments"
        r = requests.post(
            url,
            headers=self._headers(),
            params={"api-version": "7.1-preview.4"},
            json={"text": text},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def update_comment(
        self, work_item_id: int, comment_id: int, text: str
    ) -> dict[str, Any]:
        """Edit an existing comment."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}/comments/{comment_id}"
        r = requests.patch(
            url,
            headers=self._headers(),
            params={"api-version": "7.1-preview.4"},
            json={"text": text},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def delete_comment(self, work_item_id: int, comment_id: int) -> None:
        """Delete a comment from a work item."""
        url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}/comments/{comment_id}"
        r = requests.delete(
            url,
            headers=self._headers(),
            params={"api-version": "7.1-preview.4"},
            timeout=30,
        )
        r.raise_for_status()

    # -------------------------------------------------------------------------
    # Iterations / Sprints
    # -------------------------------------------------------------------------

    def get_iterations(self) -> list[dict[str, Any]]:
        """Return all iterations (sprints) for the project's default team."""
        url = f"{self.base_url}/_apis/work/teamsettings/iterations"
        r = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("value", [])

    def get_current_iteration(self) -> dict[str, Any] | None:
        """Return the current (active) iteration, or None if not found."""
        url = f"{self.base_url}/_apis/work/teamsettings/iterations"
        r = requests.get(
            url,
            headers=self._headers(),
            params={"api-version": "7.1", "$timeframe": "current"},
            timeout=30,
        )
        r.raise_for_status()
        values = r.json().get("value", [])
        return values[0] if values else None

    # -------------------------------------------------------------------------
    # Wiki
    # -------------------------------------------------------------------------

    def list_wikis(self) -> list[dict[str, Any]]:
        """Return all wikis in the project."""
        r = requests.get(
            f"{self.base_url}/_apis/wiki/wikis",
            headers=self._headers(),
            params={"api-version": "7.1"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("value", [])

    def list_wiki_pages(
        self, wiki_id: str, path: str = "/", depth: int = 2
    ) -> dict[str, Any]:
        """Return the page tree for a wiki starting at path."""
        r = requests.get(
            f"{self.base_url}/_apis/wiki/wikis/{wiki_id}/pages",
            headers=self._headers(),
            params={
                "api-version": "7.1",
                "path": path,
                "recursionLevel": str(depth),
                "includeContent": "false",
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def get_wiki_page(self, wiki_id: str, path: str) -> dict[str, Any]:
        """Fetch a wiki page and return its markdown content."""
        r = requests.get(
            f"{self.base_url}/_apis/wiki/wikis/{wiki_id}/pages",
            headers=self._headers(),
            params={
                "api-version": "7.1",
                "path": path,
                "includeContent": "true",
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    # -------------------------------------------------------------------------
    # Projects
    # -------------------------------------------------------------------------

    def list_projects(self) -> list[dict[str, Any]]:
        """Return all projects in the organization."""
        r = requests.get(
            f"{self.org_url}/_apis/projects",
            headers=self._headers(),
            params={"api-version": "7.1"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("value", [])

