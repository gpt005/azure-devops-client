# Azure DevOps Python Client

A lightweight Python client for Azure DevOps Boards using **Microsoft Entra ID (SSO) authentication** — no PATs, no stored passwords.

Authentication reuses your existing `az login` session, so corporate MFA, Conditional Access, and identity policies all apply automatically.

---

## Prerequisites

- Python 3.10+
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated
- Access to your Azure DevOps organization and project

---

## Setup

### 1. Clone / copy this folder

```bash
git clone <repo-url>
cd azure-devops-client
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
.venv\Scripts\Activate.ps1     # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Authenticate with the Azure CLI

```bash
az login
```

This opens your organization's normal Microsoft login (MFA, Conditional Access, etc.).

Verify that Azure DevOps token acquisition works:

```bash
az account get-access-token \
  --resource 499b84ac-1321-427f-aa17-267ca6975798 \
  --query accessToken \
  -o tsv
```

A long token string means you're good. A `401`/`403` means your project permissions need checking.

### 5. Set environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

Or export them directly:

```bash
# macOS / Linux
export AZDO_ORG="your-organization-name"
export AZDO_PROJECT="Your Project Name"

# Windows PowerShell
$env:AZDO_ORG = "your-organization-name"
$env:AZDO_PROJECT = "Your Project Name"
```

---

## CLI Commands

All commands accept `--org` and `--project` flags, or read from `AZDO_ORG` / `AZDO_PROJECT` environment variables.

### List all projects in the organization

```bash
python ado_client.py projects
```

### Show your open work items

```bash
python ado_client.py mine
```

### Get a work item by ID

```bash
python ado_client.py get 12345
```

### Set a work item's state

```bash
python ado_client.py state 12345 "Active"
python ado_client.py state 12345 "Resolved"
python ado_client.py state 12345 "Closed"
```

### Add a comment

```bash
python ado_client.py comment 12345 "Investigation started."
```

### Create a new work item

```bash
python ado_client.py create Task "Investigate login timeout issue"
python ado_client.py create Bug "Dashboard crashes on empty dataset"
python ado_client.py create "User Story" "As a user, I want to export reports"
```

### Run a WIQL query

```bash
python ado_client.py query "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active' ORDER BY [System.ChangedDate] DESC"

# Limit results
python ado_client.py query "SELECT [System.Id] FROM WorkItems WHERE [System.AssignedTo] = @Me" --top 20
```

### Show the current sprint / iteration

```bash
python ado_client.py sprint
```

### Explicit org/project flags (override env vars)

```bash
python ado_client.py --org my-org --project "My Project" mine
```

---

## Python API

Import and use the client directly in your own scripts:

```python
from ado_client import AzureDevOpsClient

ado = AzureDevOpsClient(
    organization="your-org",
    project="Your Project",
)

# Read
item = ado.get_work_item(12345)
print(item["fields"]["System.Title"])

# Query — @Me resolves to the authenticated identity
results = ado.my_open_items()
for item in results:
    print(item["id"], item["fields"]["System.State"], item["fields"]["System.Title"])

# Update
ado.set_state(12345, "Active")
ado.set_title(12345, "Updated title")
ado.assign_to(12345, "colleague@company.com")
ado.set_tags(12345, ["backend", "priority-high"])

# Comment
ado.add_comment(12345, "Picked up in sprint 42.")
comments = ado.get_comments(12345)

# Create
new_item = ado.create_work_item(
    work_item_type="Task",
    title="Set up CI pipeline",
    extra_fields={
        "System.AssignedTo": "you@company.com",
        "System.Tags": "devops; infra",
    },
)
print(f"Created #{new_item['id']}")

# Bulk update via raw JSON Patch
ado.update_work_item(
    12345,
    [
        {"op": "add", "path": "/fields/System.State", "value": "Resolved"},
        {"op": "add", "path": "/fields/System.Tags", "value": "done; reviewed"},
    ],
)

# Iterations
sprint = ado.get_current_iteration()
all_sprints = ado.get_iterations()
```

---

## Permissions

Authentication uses your corporate SSO identity. Two separate layers apply:

| Layer | What it controls |
|---|---|
| **Microsoft Entra** | Who you are; MFA, Conditional Access, device compliance |
| **Azure DevOps** | What you can do in each project (read, write, admin) |

For read-only operations you need view access on the project. For writes (`set_state`, `add_comment`, `create_work_item`, etc.) you need work-item edit rights in Azure DevOps.

---

## Unattended / Automation Use

`AzureCliCredential` requires an active `az login` session and is suitable for developer workstations only.

For scheduled jobs, CI/CD pipelines, or AI agents, swap the credential:

```python
from azure.identity import ManagedIdentityCredential, ClientSecretCredential

# Azure-hosted workload (VM, Container App, Azure Function, etc.)
credential = ManagedIdentityCredential()

# Service principal with client secret (store secret in Key Vault or CI secrets, never in code)
credential = ClientSecretCredential(
    tenant_id="...",
    client_id="...",
    client_secret="...",
)
```

Pass the credential to the client:

```python
ado = AzureDevOpsClient(organization="...", project="...")
ado.credential = credential   # replace after construction
```

Preference order for production: **Managed Identity > certificate-backed SP > client-secret SP > PAT**.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `CredentialUnavailableError` | Not logged in — run `az login` |
| `401 Unauthorized` from ADO API | Token acquired but ADO doesn't recognize the identity; check that your Entra account is linked to an ADO user |
| `403 Forbidden` | Authenticated but insufficient ADO project permissions |
| `404 Not Found` | Wrong org name, project name, or work item ID |
| Token acquisition works, API fails | Your enterprise may restrict third-party Azure DevOps access; contact your identity team |
