from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
from ado_client import AzureDevOpsClient

load_dotenv()


def _print_item(item: dict[str, Any]) -> None:
    f = item.get("fields", {})
    assigned = f.get("System.AssignedTo") or {}
    assignee = assigned.get("displayName", "—") if isinstance(assigned, dict) else str(assigned)
    print(
        f"  [{item['id']:>6}]"
        f"  {f.get('System.WorkItemType', '?'):14}"
        f"  {f.get('System.State', '?'):15}"
        f"  {assignee:25}"
        f"  {f.get('System.Title', '')}"
    )


def _print_item_detail(item: dict[str, Any]) -> None:
    f = item["fields"]
    assigned = f.get("System.AssignedTo") or {}
    assignee = assigned.get("displayName", "Unassigned") if isinstance(assigned, dict) else str(assigned)
    created_by = f.get("System.CreatedBy") or {}
    creator = created_by.get("displayName", "?") if isinstance(created_by, dict) else str(created_by)

    print(f"ID:          {item['id']}")
    print(f"Type:        {f.get('System.WorkItemType')}")
    print(f"Title:       {f.get('System.Title')}")
    print(f"State:       {f.get('System.State')}")
    print(f"Assigned To: {assignee}")
    print(f"Created By:  {creator}")
    print(f"Created:     {f.get('System.CreatedDate', '')[:10]}")
    print(f"Changed:     {f.get('System.ChangedDate', '')[:10]}")
    print(f"Iteration:   {f.get('System.IterationPath', '—')}")
    print(f"Area:        {f.get('System.AreaPath', '—')}")
    print(f"Tags:        {f.get('System.Tags', '—')}")
    desc = f.get("System.Description") or ""
    if desc:
        plain = re.sub(r"<[^>]+>", "", desc).strip()
        print(f"\nDescription:\n  {plain[:500]}{'...' if len(plain) > 500 else ''}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Azure DevOps work-item CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  list          List work items with optional filters
  mine          Your open work items
  sprint        Work items in the current sprint
  get           Fetch a single work item (full detail)
  create        Create a new work item
  title         Update a work item's title
  description   Set / replace a work item's description
  state         Change a work item's state
  assign        Assign a work item to someone
  tags          Set tags on a work item
  parent        Set the parent of a work item
  delete        Delete a work item (soft by default)
  restore       Restore a soft-deleted work item
  comments      List all comments on a work item
  comment add   Add a comment
  comment edit  Edit an existing comment
  comment del   Delete a comment
  query         Run a raw WIQL query
  sprints       List all iterations / sprints
  projects      List all projects in the organization
""",
    )
    parser.add_argument("--org", default=os.environ.get("AZDO_ORG"))
    parser.add_argument("--project", default=os.environ.get("AZDO_PROJECT"))
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List work items with filters")
    p_list.add_argument("--type", dest="work_item_type", help="e.g. Task, Bug, User Story")
    p_list.add_argument("--state", help="e.g. Active, New, Resolved, Closed")
    p_list.add_argument("--assigned", dest="assigned_to", help="email or 'me'")
    p_list.add_argument("--tag", dest="tags", action="append", help="Filter by tag (repeatable)")
    p_list.add_argument("--area", dest="area_path")
    p_list.add_argument("--iteration", dest="iteration_path")
    p_list.add_argument("--top", type=int, default=50)

    # mine
    p_mine = sub.add_parser("mine", help="Your open work items")
    p_mine.add_argument("--top", type=int, default=50)

    # sprint
    p_sprint = sub.add_parser("sprint", help="Work items in the current sprint")
    p_sprint.add_argument("--iteration", dest="iteration_path", help="Override sprint path")
    p_sprint.add_argument("--top", type=int, default=50)

    # get
    p_get = sub.add_parser("get", help="Fetch a work item")
    p_get.add_argument("id", type=int)

    # create
    p_create = sub.add_parser("create", help="Create a new work item")
    p_create.add_argument("type", help="Work item type, e.g. Task, Bug")
    p_create.add_argument("title")
    p_create.add_argument("--description", "-d")
    p_create.add_argument("--assign", dest="assigned_to", metavar="EMAIL")
    p_create.add_argument("--tag", dest="tags", action="append")
    p_create.add_argument("--area", dest="area_path")
    p_create.add_argument("--iteration", dest="iteration_path")
    p_create.add_argument("--parent", dest="parent_id", type=int, metavar="ID", help="Work item ID to set as parent")

    # title
    p_title = sub.add_parser("title", help="Update a work item's title")
    p_title.add_argument("id", type=int)
    p_title.add_argument("title")

    # description
    p_desc = sub.add_parser("description", help="Set a work item's description")
    p_desc.add_argument("id", type=int)
    p_desc.add_argument("text")

    # state
    p_state = sub.add_parser("state", help="Change work item state")
    p_state.add_argument("id", type=int)
    p_state.add_argument("state", help="e.g. Active, Resolved, Closed")

    # assign
    p_assign = sub.add_parser("assign", help="Assign a work item")
    p_assign.add_argument("id", type=int)
    p_assign.add_argument("email")

    # tags
    p_tags = sub.add_parser("tags", help="Set tags on a work item (replaces existing)")
    p_tags.add_argument("id", type=int)
    p_tags.add_argument("tags", nargs="+", help="One or more tags")

    # parent
    p_parent = sub.add_parser("parent", help="Set the parent of a work item")
    p_parent.add_argument("id", type=int, help="Child work item ID")
    p_parent.add_argument("parent_id", type=int, help="Parent work item ID")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a work item")
    p_delete.add_argument("id", type=int)
    p_delete.add_argument(
        "--destroy",
        action="store_true",
        help="Permanently destroy instead of soft-delete",
    )

    # restore
    p_restore = sub.add_parser("restore", help="Restore a soft-deleted work item")
    p_restore.add_argument("id", type=int)

    # comments
    p_comments = sub.add_parser("comments", help="List comments on a work item")
    p_comments.add_argument("id", type=int)

    # comment add / edit / del
    p_comment = sub.add_parser("comment", help="Add, edit, or delete a comment")
    comment_sub = p_comment.add_subparsers(dest="comment_action")
    ca = comment_sub.add_parser("add", help="Add a comment")
    ca.add_argument("id", type=int)
    ca.add_argument("text")
    ce = comment_sub.add_parser("edit", help="Edit a comment")
    ce.add_argument("id", type=int, help="Work item ID")
    ce.add_argument("comment_id", type=int)
    ce.add_argument("text")
    cd = comment_sub.add_parser("del", help="Delete a comment")
    cd.add_argument("id", type=int, help="Work item ID")
    cd.add_argument("comment_id", type=int)

    # query
    p_query = sub.add_parser("query", help="Run a raw WIQL query")
    p_query.add_argument("wiql")
    p_query.add_argument("--top", type=int, default=50)

    # sprints
    sub.add_parser("sprints", help="List all iterations / sprints")

    # projects
    sub.add_parser("projects", help="List all projects in the organization")

    args = parser.parse_args()

    if not args.org or not args.project:
        parser.error(
            "Set AZDO_ORG and AZDO_PROJECT in your .env file or pass --org / --project."
        )

    ado = AzureDevOpsClient(organization=args.org, project=args.project)

    match args.command:
        case "list":
            items = ado.list_work_items(
                work_item_type=args.work_item_type,
                state=args.state,
                assigned_to=args.assigned_to,
                tags=args.tags,
                area_path=args.area_path,
                iteration_path=args.iteration_path,
                top=args.top,
            )
            print(f"{len(items)} item(s):\n")
            for item in items:
                _print_item(item)

        case "mine":
            items = ado.my_open_items(top=args.top)
            print(f"{len(items)} open item(s) assigned to you:\n")
            for item in items:
                _print_item(item)

        case "sprint":
            items = ado.list_by_sprint(
                iteration_path=getattr(args, "iteration_path", None),
                top=args.top,
            )
            print(f"{len(items)} item(s) in current sprint:\n")
            for item in items:
                _print_item(item)

        case "get":
            _print_item_detail(ado.get_work_item(args.id))

        case "create":
            item = ado.create_work_item(
                work_item_type=args.type,
                title=args.title,
                description=getattr(args, "description", None),
                assigned_to=getattr(args, "assigned_to", None),
                tags=getattr(args, "tags", None),
                area_path=getattr(args, "area_path", None),
                iteration_path=getattr(args, "iteration_path", None),
            )
            item_id = item["id"]
            print(f"Created {args.type} #{item_id}: {args.title}")
            if getattr(args, "parent_id", None):
                ado.set_parent(item_id, args.parent_id)
                print(f"Parent set to #{args.parent_id}.")

        case "title":
            ado.set_title(args.id, args.title)
            print(f"Work item {args.id} title updated.")

        case "description":
            ado.set_description(args.id, args.text)
            print(f"Work item {args.id} description updated.")

        case "state":
            ado.set_state(args.id, args.state)
            print(f"Work item {args.id} state set to '{args.state}'.")

        case "assign":
            ado.assign_to(args.id, args.email)
            print(f"Work item {args.id} assigned to {args.email}.")

        case "tags":
            ado.set_tags(args.id, args.tags)
            print(f"Work item {args.id} tags set to: {', '.join(args.tags)}")

        case "parent":
            ado.set_parent(args.id, args.parent_id)
            print(f"Work item #{args.id} parent set to #{args.parent_id}.")

        case "delete":
            action = "permanently destroyed" if args.destroy else "soft-deleted (in recycle bin)"
            ado.delete_work_item(args.id, destroy=args.destroy)
            print(f"Work item {args.id} {action}.")

        case "restore":
            ado.restore_work_item(args.id)
            print(f"Work item {args.id} restored.")

        case "comments":
            comments = ado.get_comments(args.id)
            print(f"{len(comments)} comment(s) on #{args.id}:\n")
            for c in comments:
                author = c.get("createdBy", {}).get("displayName", "?")
                date = c.get("createdDate", "")[:10]
                text = re.sub(r"<[^>]+>", "", c.get("text", "")).strip()
                print(f"  [{c['id']}] {author} on {date}")
                print(f"       {text[:200]}")
                print()

        case "comment":
            match args.comment_action:
                case "add":
                    ado.add_comment(args.id, args.text)
                    print(f"Comment added to #{args.id}.")
                case "edit":
                    ado.update_comment(args.id, args.comment_id, args.text)
                    print(f"Comment {args.comment_id} on #{args.id} updated.")
                case "del":
                    ado.delete_comment(args.id, args.comment_id)
                    print(f"Comment {args.comment_id} on #{args.id} deleted.")
                case _:
                    p_comment.print_help()

        case "query":
            items = ado.query_work_items(args.wiql, top=args.top)
            print(f"{len(items)} result(s):\n")
            for item in items:
                _print_item(item)

        case "sprints":
            for it in ado.get_iterations():
                attrs = it.get("attributes", {})
                start = (attrs.get("startDate") or "")[:10]
                end = (attrs.get("finishDate") or "")[:10]
                print(f"  {it['name']:30}  {start} → {end}  {it['path']}")

        case "projects":
            for p in ado.list_projects():
                print(f"  {p['name']}")

        case _:
            parser.print_help()
