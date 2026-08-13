# Wiki Governance

*Conventions for creating, naming, and structuring wiki pages in the Agent Assurance All Towers project. Apply before creating any new page. See also [Boards Governance](/Standards-%26-Process/Boards-Governance).*

---

## 0. Before Creating a Page

1. Identify the correct parent section — where does this page belong?
2. Check Rule 1 to decide whether the page is a flat sibling or triggers folder promotion.
3. Check Rule 2 to decide whether the content warrants a three-page triad.
4. After creating the page, update the parent index page (Rule 10 — mandatory).

---

## 1. Folder vs. Flat Siblings

| Condition | Structure |
|---|---|
| 1–3 related pages | Flat siblings with a shared name prefix (e.g. `CI-CD Pipeline`, `CI-CD Contracts`, `CI-CD Decisions`) |
| 4+ related pages, or contracts have their own sub-pages | Promote to a folder with an index page at its root |

A folder **must** have an index page with the same name as the folder. The index page is the navigation hub; sub-pages hold the detail. Sub-pages of a folder are listed on that folder's own index, not on the grandparent's index.

---

## 2. The Three-Page Triad

Every significant system, pipeline, or cross-team interface gets three pages:

| Page | Purpose | What belongs here |
|---|---|---|
| **Design** — `Feature Name` | Current state; how it works | Flows, tables, diagrams, configuration |
| **Contracts** — `Feature Name Contracts` | Formal guarantees, numbered `C1, C2, …` | What it promises; conditions; failure behaviour |
| **Decisions** — `Feature Name Decisions` | Numbered rationale, immutable once published | What was decided and why; superseded entries struck through |

Apply this triad when documenting: a pipeline, a service API, an auth flow, a data schema, or any interface other teams build against.

The design page must not explain *why* — rationale belongs exclusively in the Decisions page.

---

## 3. Page Header Format

```markdown
# Page Title

*One-sentence scope statement. Companion to [Sibling A](/absolute/path) and [Sibling B](/absolute/path).*

---

## 0. Prerequisites   ← only when there is a mandatory gate before acting
## 1. First Section
## 2. Second Section
```

Rules:
- H1 must match the page title exactly
- The italic companion line is required on any page that has siblings (triad members or folder sub-pages with related content)
- `---` separates the header from the body
- Sections are numbered `## N.` starting from `1`; use `## 0.` only for prerequisite or gate sections
- No "last updated", "version", or "author" lines — the wiki's Git history is the audit trail

---

## 4. Contracts Page Rules

```markdown
## C1 — Contract name

**The system never deploys X without Y.**

| Condition | Behaviour |
|---|---|
| condition A | result A |
| condition B | result B |
```

- Each contract opens with a bold guarantee statement in declarative, imperative language ("The pipeline never…", "Every merge produces…")
- The guarantee is followed by a conditions table
- Numbered `C1, C2, …` in the order ratified — never renumbered
- A changed contract gets a new number; the old entry adds `*(superseded by CN)*`
- No rationale on this page — that belongs in the companion Decisions page

---

## 5. Decisions Page Rules

```markdown
| # | Decision | Rationale |
|---|---|---|
| P1 | **Bold statement of the decision made** | One-sentence reason |
```

Domain prefixes:

| Prefix | Domain |
|---|---|
| `P` | Pipeline |
| `I` | Infrastructure |
| `D` | API / data design |
| `A` | Architecture |
| `S` | Security |
| `G` | Governance / process |

Rules:
- The Decision column is the **what**; Rationale is the **why**
- Options considered but not chosen are not recorded here — only the decision taken
- Numbers are frozen once published; superseded entries: ~~P3~~ *(superseded by P11)*

---

## 6. Naming Rules

| Rule | Correct | Incorrect |
|---|---|---|
| Title case, noun phrases | `Scanner Distribution` | `Distributing Scanners` |
| No dates in page titles | `Decision Log` | `Decisions Aug 2026` |
| No "How to" at folder level | `Git & Branching` | `How to Use Git` |
| Prefix flat siblings consistently | `CI-CD Pipeline`, `CI-CD Contracts` | `Pipeline`, `CI-CD Contracts` |
| "Start Here" is reserved for the first navigation page in a workstream folder | — | Any other use |

---

## 7. Link Format

Use absolute paths from the wiki root — hyphens for spaces, `%26` for `&`. Never use relative `./page` paths; ADO wiki does not resolve them from index pages.

```
/Standards-%26-Process/Wiki-Governance
/Standards-%26-Process/CI-CD/CI-CD-Contracts
/Migration-and-Self%2Dservice/Platform-Spec/Contracts/02-Scan-Transaction
```

---

## 8. Content Rules

- **Tables over prose lists** — any set of 3+ structured items goes in a table
- **ASCII or Mermaid diagrams for flows** — use fenced code blocks for pipeline flows, hierarchies, and sequences
- **Design pages describe current state only** — if you are explaining *why*, move it to the Decisions page
- **Contracts pages use imperative language** — "The pipeline never…", not "We try to avoid…"
- **No orphan pages** — every page must be linked from its parent index page or a "Start Here" page

---

## 9. When to Create Each Page Type

| You are documenting… | Create |
|---|---|
| A new system, pipeline, or service interface | Design + Contracts + Decisions triad |
| A process or standard people must follow | A page under `Standards & Process` |
| A workstream's scope and status | Pages under a workstream folder with a "Start Here" |
| A team admin or HR topic | Under `Team Operations` (not at the wiki root) |
| An API or data schema | A Contracts sub-page under the relevant feature folder |

---

## 10. Parent Index Rule

**Every time you create or delete a page, you must update its parent's index page in the same operation.**

The parent index page is the page with the same name as the containing folder (e.g. `Standards & Process` is the index for all pages directly under `/Standards & Process/`).

Under the `## Pages` section of the parent index, add one line per direct child page:

```markdown
## Pages

- [Page Title](/Absolute/Path/To/Page) — One-sentence description of what the page covers.
```

Rules:
- List direct child pages only — sub-pages of sub-folders appear on that sub-folder's own index
- The description is one sentence ending with a full stop
- Pages are listed in logical reading order, not alphabetical order
- Deleting a page requires removing its entry from the parent index in the same operation
