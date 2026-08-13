# Vasili's Wiki Conventions

Conventions observed in the live wiki pages authored and maintained by Vasili Ramanishka.
Use this as a reference when authoring new pages so content fits the established style.

---

## 1 · Page structure

- H1 must match the page title exactly
- Optional bold status/date line immediately under H1:
  `**Approved in session 2026-07-28.**`
- Optional italic companion/scope line:
  `*Companion to [PageA](/path) and [PageB](/path).*`
- `---` separator before the first section
- Sections are `## N · Title` (en-dot, not period): `## 0 · Decisions`, `## 1 · Why…`
- Section `## 0 ·` is reserved for an embedded decisions table when present — not a prerequisite gate

---

## 2 · Architecture pages — single document, decisions embedded

Each page under `/Migration and Self-service/Architecture/` is **one self-contained document**.
Decisions live inside the page in a table under `## 0 · Decisions`:

```markdown
| # | Decision | Rationale |
|---|---|---|
| **A1** | **Bold statement of the decision** | One-sentence reason |
```

- Prefix `A` = Architecture. A-numbers are local to that page, not globally unique across the wiki.
- There are no companion "…Contracts" or "…Decisions" sibling pages for architecture docs.
  All rationale lives in the main page.
- Superseded entries: ~~A3~~ *(superseded by A9)* inline.

---

## 3 · Platform Spec — centralised contracts + one decision log

A different model from Architecture, used only for the Platform Spec section:

- **One index page** (`Contracts`) with a status/protocol header and a table of all contract files
- **Individual contract sub-pages**, numbered `01 Identity Auth`, `02 Scan Transaction`…
  Each opens with `**Owner:** … **Status:** … **Depends on:** …` then numbered prose sections.
  No C-prefixed items within them.
- **One central Decision Log** holding all D-numbered decisions for the entire section.
  D-numbers are globally unique across the Platform Spec section.

---

## 4 · Decision numbering

| Prefix | Domain | Location |
|---|---|---|
| `A` | Architecture | Embedded table in each Architecture page |
| `D` | API / data design | Platform Spec Decision Log (one central page) |

Numbers are never reused. Superseded entries use strikethrough inline:

```
~~D2~~ **SUPERSEDED by D19 (2026-07-28).** Reason in one sentence.
```

---

## 4a · No C-numbering on contracts pages

Vasili's existing section style (`## N · Title`) already provides unambiguous numbering for any
contracts page. Do not use `C1, C2, …` prefixes — they create cross-section ambiguity (2026-08-13
incident: Standards & Process was unpublished because CI-CD Contracts' `C1–C10` collided
conversationally with Platform Spec contract references).

**Follow the existing `## N · Title` convention for all contract sections:**

```markdown
## 1 · Build integrity
## 2 · Immutability
## 3 · Environment promotion
```

The Platform Spec uses page-level numbering (`01 Identity Auth`, `02 Scan Transaction`…) rather than
C-prefixed sections within pages — that established pattern should not be changed.

---

## 5 · Link format

Bare markdown: `[Title](/Path-To-Page)`. Rules:

- Hyphens for spaces in path segments
- `%2D` for a literal hyphen **within** a word (e.g. `Self%2Dservice` for "Self-service")
- `%26` for `&` (e.g. `Standards-%26-Process`)
- No trailing slashes; no relative `./` paths

Example from a live page:

```
[Agentic Delivery Model](/Migration-and-Self%2Dservice/Architecture/Agentic-Delivery-Model)
```

---

## 6 · What Vasili does NOT do

- Architecture pages do **not** have separate Contracts or Decisions companion pages.
- Architecture pages do **not** use C-numbered contracts internally.
- The Platform Spec Decision Log is D-numbers only — not a catch-all for all wiki decisions.
- No "last updated", "author", or "version" headers — git history is the audit trail.
- Section numbers use `## N ·` not `## N.` (en-dot with spaces, not period).
- No orphan cross-section numbering: A-numbers are page-local, D-numbers are Platform Spec-local.
