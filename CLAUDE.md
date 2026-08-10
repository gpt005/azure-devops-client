# Azure DevOps Client

Python CLI and library for Azure DevOps Boards via Microsoft Entra ID (SSO) — no PATs.

## Auth

Requires an active `az login` session. Credentials are never stored in code.

```bash
az login
```

## Environment

Set in `.env` (gitignored):

```env
AZDO_ORG=AGENTASSURANCE01
AZDO_PROJECT=Agent Assurance All Towers
```

Available projects in `AGENTASSURANCE01`:

- `Agent Assurance All Towers`
- `AGENTASSURANCE01`
- `AgentGovernance`

To target a different project ad-hoc, pass `--project "AgentGovernance"` on the command line. If the user mentions a project by name, add `--project "<name>"` to the command.

## Entry point

`ado_client.py` is both the library (`AzureDevOpsClient`) and the CLI (`python ado_client.py <command>`).

## Run

```bash
python ado_client.py --help
```

## Key conventions

- All writes use JSON Patch (`application/json-patch+json`)
- WIQL queries return IDs only; a second request fetches fields — `query_work_items` handles both steps
- `set_field(id, "System.FieldName", value)` is the generic updater; named helpers delegate to it
- Descriptions accept plain text or HTML (Azure DevOps stores HTML internally)
- Soft-delete moves items to the recycle bin; `--destroy` is permanent and irreversible
