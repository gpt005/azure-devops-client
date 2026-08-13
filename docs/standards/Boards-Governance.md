# Boards Governance

*Formalised Azure DevOps Boards conventions for the Agent Assurance All Towers project. Effective immediately.*

---

## 0. Before You Create a Ticket

Consult the wiki **before** opening any work item. This prevents misalignment with binding decisions and avoids duplicates.

### Required reading by item type

| Creating a… | Check first |
|---|---|
| **Epic / Feature** | [Platform Spec index](/Migration-and-Self%2Dservice/Platform-Spec) · [Contracts index](/Migration-and-Self%2Dservice/Platform-Spec/Contracts) · [Decision Log](/Migration-and-Self%2Dservice/Platform-Spec/Decision-Log) · [Architecture](/Migration-and-Self%2Dservice/Architecture) |
| **User Story / Task** | The binding contract for your workstream (see coverage map below) · any open D-numbered decisions in the [Decision Log](/Migration-and-Self%2Dservice/Platform-Spec/Decision-Log) that affect your area |
| **Bug** | The binding contract that defines the expected behaviour your bug violates |

### Workstream → contract coverage map

| Workstream | Binding contract(s) |
|---|---|
| WS1 + WS2 — Bundle build & distribution | [04 Scanner Distribution](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/04-Scanner-Distribution) |
| WS3 — Scan transaction | [02 Scan Transaction](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/02-Scan-Transaction) · [DB Platform Metadata](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/DB-Platform-Metadata) |
| WS4 — Evidence ingestion | [03 Evidence Ingestion](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/03-Evidence-Ingestion) |
| WS5 + WS5A — Findings / verdict + catalog | [05 FPA Service](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/05-FPA-Service) · [DB Findings Register](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/DB-Findings-Register) |
| WS6 + WS7 — Governance + portal | [06 Portal Workbench](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/06-Portal-Workbench) |
| WS8 — Client integration (AEC SDK) | [07 AEC Protocol](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/07-AEC-Protocol) · [Architecture → Client Integration](/Migration-and-Self%2Dservice/Architecture) |
| WS9 — Identity + deployment | [01 Identity Auth](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/01-Identity-Auth) · [Architecture → Platform Deployment](/Migration-and-Self%2Dservice/Architecture) |
| Cross-cutting trust architecture | [08 Three-Channel](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/08-Three-Channel) |
| LLM inference | [09 Inference Proxy](/Migration-and-Self%2Dservice/Platform-Spec/Contracts/09-Inference-Proxy) |

### What to capture in the ticket

After reading the relevant wiki pages, carry the following forward into the description (see templates in §3):

- **Wiki links** — direct links to every contract or page that governs this item
- **Relevant decisions** — D-numbers from the Decision Log that constrain design or acceptance criteria
- **Delivery tier** — Go-live (Aug 15), Deck-complete (Aug 31), or Hardening (undated), per the Contracts index

---

## 1. Work Item Hierarchy

```
Epic
 └── Feature
      └── User Story
           └── Task

Bug  ←── must be linked to a Feature (or Epic if no Feature exists)
```

Bugs are **not** a parallel track. Every bug must be parented to a Feature so defects trace back to an initiative. If no Feature exists for a bug, create one first.

### When to use each type

| Type | Use when | Scope |
|---|---|---|
| **Epic** | A major programme outcome spanning multiple sprints and teams | Quarter or programme increment |
| **Feature** | A deliverable capability within an Epic, completable in 1–3 sprints | Sprint group |
| **User Story** | A discrete slice of value, completable within one sprint | Single sprint |
| **Task** | A concrete unit of work, completable by one person in under 2 days | Within a sprint |
| **Bug** | A deviation from accepted behaviour on a shipped or in-review item | Within a sprint |

### Mandatory fields by type

| Field | Epic | Feature | User Story | Task | Bug |
|---|---|---|---|---|---|
| Title | ✓ | ✓ | ✓ | ✓ | ✓ |
| Description | ✓ | ✓ | ✓ | ✓ | ✓ |
| Area Path | ✓ | ✓ | ✓ | ✓ | ✓ |
| Parent link | — | Epic | Feature | User Story | Feature |
| Iteration Path | Root | Root | Sprint | Sprint | Sprint |
| Story Points | — | — | ✓ | — | — |
| Acceptance Criteria | — | — | ✓ | — | ✓ |
| Tags | ✓ | ✓ | ✓ | optional | ✓ |
| Assigned To | — | ✓ | ✓ | ✓ | ✓ |

Epics and Features float at the root iteration path intentionally — they are roadmap items, not sprint commitments.

---

## 2. Title Conventions

- **No personal names in titles** — the title must describe the deliverable, not the assignee
- Title case throughout; no trailing punctuation
- Em-dash is `—` (not a hyphen or `--`)

| Type | Format | Example |
|---|---|---|
| **Epic** | Plain noun phrase | `Self-Service Onboarding` |
| **Feature** | `Domain — Deliverable (qualifier)` | `Self Service — Presenter Onboarding Flow (v1)` |
| **User Story** | `As a [role], I can [action]` (≤80 chars) | `As a lead presenter, I can upload a spec and trigger evaluation` |
| **Task** | `Tn — Action phrase` or standalone phrase | `T1 — Define evaluation schema` |
| **Bug** | `[Component] — Short broken-behaviour statement` | `Onboarding — SSO redirect loop on first login` |

---

## 3. Description Templates

All templates include a **References** section. Populate it with links to the wiki pages and decision log entries you consulted before creating the ticket (§0). Leave it blank only if the item is genuinely uncovered by any wiki page — that itself is worth noting.

### Epic

```
## Purpose
[What programme outcome does this deliver? Why does it matter?]

## Context
[Background, constraints, dependencies.]

## Success Criteria
- [Measurable outcome 1]

## Out of Scope
- [Explicit exclusion]

## References
- Wiki: [page title](wiki-link)
- Decision Log: D-number — brief description (if applicable)
- Delivery tier: [Go-live / Deck-complete / Hardening]
```

### Feature

```
## What this is
[One sentence. The deliverable in plain English.]

## Scope
| In | Out |
|---|---|
| [In scope item] | [Out of scope item] |

## Acceptance Criteria
- Given [context], when [action], then [outcome]

## Dependencies
- [Blocking item]

## References
- Contract: [contract name](wiki-link) — section [N] (if applicable)
- Decision Log: D-number — brief description (if applicable)
- Delivery tier: [Go-live (Aug 15) / Deck-complete (Aug 31) / Hardening]
```

### User Story

```
## Story
**As a** [role]
**I want** [capability]
**So that** [business value]

## Acceptance Criteria
- Given [context], when [action], then [outcome]
- Given [edge case], when [action], then [expected handling]

## Detail
[Additional context, wireframes, edge cases]

## References
- Contract: [contract name](wiki-link) — section or endpoint (if applicable)
- Decision Log: D-number — brief description (if applicable)
```

### Task

```
## Action
[What specifically needs to be done.]

## Why it matters
[What breaks or stalls if this is skipped.]

## Done when
- [Specific, verifiable completion condition]

## References
- Contract / wiki: [link] (if applicable)
```

### Bug

```
## Steps to Reproduce
1. [Step 1]
2. [Observed result]

## Expected vs Actual
**Expected:** [what should happen]
**Actual:** [what happens, with error messages]

## Impact
Severity: [Critical / High / Medium / Low]
Environment: [dev / staging / prod]

## References
- Contract violated: [contract name](wiki-link) — section that defines the expected behaviour
- Decision Log: D-number (if a decision governs this behaviour)
```

---

## 4. Tag Taxonomy

All tags: lowercase, hyphenated, semicolon-separated. **Only use tags from this list.** New tags require team sign-off before use.

### Workstream (exactly one required per item)

| Tag | Meaning |
|---|---|
| `ws-self-service` | Self Service tower |
| `ws-assurance-data` | Assurance Data and Processes |
| `ws-spec-review` | Spec Review capability |
| `ws-governance` | AgentGovernance cross-cutting |
| `ws-platform` | Platform / infrastructure |

### Work type

| Tag | Meaning |
|---|---|
| `spec-review` | Related to the spec review process |
| `rehearsal` | Rehearsal or run-through activity |
| `onboarding` | Team or presenter onboarding |
| `alignment` | Cross-team or stakeholder alignment |
| `infra` | Infrastructure, environment, or tooling |
| `documentation` | Wiki, runbook, or artefact creation |
| `testing` | Test creation or execution |
| `security` | Security, auth, or compliance item |

### Priority signal (use sparingly)

| Tag | Meaning |
|---|---|
| `blocker` | Blocking another team or sprint |
| `go-live-risk` | Directly threatens go-live readiness |
| `client-facing` | Visible to the client; higher scrutiny |

### State signal

| Tag | Meaning |
|---|---|
| `awaiting-sign-off` | Complete but pending approval |
| `needs-refinement` | Story not ready for sprint |
| `carry-over` | Moved from a previous sprint incomplete |

### Legacy tag migrations

| Old tag | Replace with |
|---|---|
| `high` | Set the **Priority** field to `1 - Critical` |
| `portable-harness` | `ws-platform; infra` |
| `alignment-enhancement` | `alignment` |
| `ws1` / `ws2` / `ws3` | `ws-self-service` / `ws-assurance-data` / `ws-spec-review` |

---

## 5. Area Path Governance

| Area Path | Owns |
|---|---|
| `Agent Assurance All Towers` | Root only. Epics spanning all towers. Not a dumping ground. |
| `...\Self Service` | Self Service tower items |
| `...\Assurance Data and Processes` | Data pipelines, evidence packs, reporting |
| `...\Spec Review` | Spec review capability and evaluation harness |
| `...\Governance` | AgentGovernance cross-cutting items |
| `...\Platform` | Infrastructure, auth, shared tooling |

**Rules:**
- Every item below Epic level must have a non-root area path assigned at creation.
- Area path is set by the team lead or scrum master at creation or during refinement.
- Items spanning two area paths go under the primary consumer; note the secondary in the description.
- Bugs inherit their parent Feature's area path.

---

## 6. Sprint Cadence

**Sprint length: 2 weeks**

### Naming convention

```
[Phase] — Sprint [N] (DD Mon – DD Mon YYYY)

Post-MVP — Sprint 1 (01 Sep – 12 Sep 2026)
Post-MVP — Sprint 2 (15 Sep – 26 Sep 2026)
```

Reset the counter and prefix when the programme phase changes.

**Rule:** Always keep at least 3 sprints defined ahead. Never let the next sprint be undefined at the start of the current one.

### What belongs where

| In sprint | In backlog (root iteration) |
|---|---|
| User Stories committed this sprint | Epics (roadmap items) |
| Tasks attached to committed stories | Features (not yet broken into stories) |
| Bugs being actively fixed | Unrefined User Stories |
| | Untriaged Bugs |

---

## 7. Definition of Done

### Epic
- [ ] All child Features are `Closed` or `Resolved`
- [ ] Success criteria in the description are demonstrably met
- [ ] Stakeholder sign-off documented (link to email or wiki)

### Feature
- [ ] All child User Stories are `Closed`
- [ ] Acceptance criteria verified and passed
- [ ] No open bugs parented to this Feature at severity High or above
- [ ] Demo or walkthrough completed with stakeholders
- [ ] Area path and tags correctly set

### User Story
- [ ] All acceptance criteria checking and passing
- [ ] Code reviewed and approved (minimum 1 reviewer)
- [ ] Tests written and passing in CI (where applicable)
- [ ] Story Points entered
- [ ] Area path, tags, sprint, and parent Feature all set
- [ ] No incomplete child Tasks

### Task
- [ ] "Done when" conditions in the description are met
- [ ] Output handed off or documented for the next person
- [ ] Assigned to a real person (not Unassigned)

### Bug
- [ ] Root cause identified and documented
- [ ] Fix implemented and code reviewed
- [ ] Regression test added (or reason documented why not feasible)
- [ ] Verified fixed in the environment where reported
- [ ] Linked to parent Feature
