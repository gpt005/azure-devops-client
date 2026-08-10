Interact with Azure DevOps Boards using natural language. The argument describes what to do.

The CLI is `python tools/boards.py` in this directory. Auth uses `az login` — no PATs.

## Operations

**Read**
- `python tools/boards.py mine` — my open items
- `python tools/boards.py sprint` — current sprint items
- `python tools/boards.py get <id>` — single item detail
- `python tools/boards.py list [--type Bug] [--state Active] [--assigned me] [--tag x] [--top 20]`
- `python tools/boards.py query "<WIQL>"` — raw WIQL query

**Create**
- `python tools/boards.py create <Type> "<title>" [--description "..."] [--assign email] [--tag x]`

**Update**
- `python tools/boards.py title <id> "<new title>"`
- `python tools/boards.py description <id> "<text>"`
- `python tools/boards.py state <id> "<state>"` — e.g. Active, Resolved, Closed
- `python tools/boards.py assign <id> <email>`
- `python tools/boards.py tags <id> tag1 tag2`

**Delete / Restore**
- `python tools/boards.py delete <id>` — soft-delete (recycle bin)
- `python tools/boards.py delete <id> --destroy` — permanent, irreversible
- `python tools/boards.py restore <id>`

**Comments**
- `python tools/boards.py comments <id>` — list
- `python tools/boards.py comment add <id> "<text>"`
- `python tools/boards.py comment edit <id> <comment_id> "<text>"`
- `python tools/boards.py comment del <id> <comment_id>`

**Other**
- `python tools/boards.py sprints` — list all iterations
- `python tools/boards.py projects` — list all projects

**Wiki** (separate tool: `tools/wiki.py`)
- `python tools/wiki.py list` — list all wikis
- `python tools/wiki.py pages [--depth N] [--path /Some/Path]` — browse page tree
- `python tools/wiki.py read <path>` — read a page's markdown content

## Instructions

Translate the user's request ($ARGUMENTS) into the right command(s) and run them.
For WIQL queries always include `[System.TeamProject] = @project` and `ORDER BY [System.ChangedDate] DESC`.
After creating an item, show the ID and link: `https://dev.azure.com/{org}/{project}/_workitems/edit/{id}`.
For wiki requests, use `tools/wiki.py` instead of `tools/boards.py`.
