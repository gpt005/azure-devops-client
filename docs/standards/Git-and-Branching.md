# Git & Branching

*Branching conventions, commit standards, and PR process for all repositories under the Agent Assurance All Towers project. Effective immediately.*

---

## 1. Branch Model

All repositories use **trunk-based development** off `main`.

```
main  ←── always deployable; protected; no direct pushes
 ├── feature/short-description
 ├── bugfix/short-description
 ├── chore/short-description
 └── hotfix/short-description
```

`main` is the only long-lived branch. Feature branches are short-lived (ideally < 3 days). No `develop`, `staging`, or `release` branches.

### Branch naming

```
<type>/<slug>
```

| Prefix | When to use |
|---|---|
| `feature/` | New capability or enhancement |
| `bugfix/` | Fix for a defect |
| `hotfix/` | Urgent fix that must go straight to production |
| `chore/` | Tooling, config, dependency updates, refactors with no behaviour change |
| `docs/` | Documentation-only changes |

**Rules:**
- All lowercase; hyphens only (no underscores, no slashes beyond the prefix)
- No personal names, ticket numbers as prefixes, or dates in branch names
- Keep the slug short (≤ 5 words): `feature/presenter-onboarding-flow`, not `feature/gary-adds-the-new-onboarding-flow-for-presenters`
- Include the ADO work item ID in the PR, not the branch name

---

## 2. Commit Messages

Follow **Conventional Commits** format:

```
<type>(<scope>): <short summary>

[optional body]

[optional footer: Refs #<ADO-item-id>]
```

### Type

| Type | When |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change with no behaviour change |
| `test` | Adding or correcting tests |
| `docs` | Documentation only |
| `chore` | Build, config, dependency changes |
| `perf` | Performance improvement |

### Rules
- Summary line ≤ 72 characters; imperative mood ("add", not "added" or "adds")
- No full stop at the end of the summary line
- Body explains *why*, not *what* — the diff already shows what changed
- Reference the ADO item in the footer: `Refs #1234`

**Examples:**
```
feat(onboarding): add SSO redirect handling for first-time presenters

Refs #1042

fix(eval): correct schema validation for nested agent responses

The previous check only validated top-level fields; nested `output`
blocks were silently accepted regardless of type.

Refs #1089
```

---

## 3. Pull Requests

### Before opening a PR
- [ ] Branch is up to date with `main` (rebase preferred over merge)
- [ ] All tests pass locally
- [ ] No debug code, commented-out blocks, or `TODO` left without a linked ADO item
- [ ] Self-review completed (read your own diff before requesting review)

### PR title

Match the commit format: `<type>(<scope>): <summary>`. Keep it under 72 characters.

```
feat(spec-review): add evaluation harness dry-run mode
fix(auth): resolve token refresh race condition on session expiry
```

### PR description template

```markdown
## What this does
[One or two sentences. The deliverable in plain English.]

## Why
[Motivation. Link to the relevant ADO work item: #1234]

## How to test
[Steps a reviewer can follow to verify the change works.]

## Checklist
- [ ] Tests added or updated
- [ ] Docs updated (if applicable)
- [ ] ADO work item linked
```

### Review rules

| Rule | Detail |
|---|---|
| Minimum approvals | 1 for most PRs; 2 for changes to auth, infra, or shared config |
| Author cannot self-approve | Even if you are the only reviewer available |
| No merging with unresolved comments | Resolve or explicitly defer with a linked ADO item |
| Review SLA | Reviewers respond within 1 business day; escalate if blocked |

### Merge strategy

**Squash and merge** is the default for all PRs into `main`.

- Keeps `main` history linear and readable
- The squash commit message should be the PR title (CI enforces this)
- Exception: large, multi-commit PRs where preserving atomic history has value — use **merge commit** with team lead approval

---

## 4. Branch Protection (main)

| Rule | Setting |
|---|---|
| Direct push | Blocked for all, including admins |
| PR required | Yes — minimum 1 approval |
| CI must pass | Yes — all status checks must be green |
| Delete branch on merge | Yes (automatic) |
| Linear history | Required (no merge commits into main without squash) |

---

## 5. Keeping Branches Fresh

- Rebase onto `main` at least once per day on active branches
- If your branch is more than 5 days old without a PR, flag it in standup
- Stale branches (no commits for 14+ days) will be pruned without notice — open a PR or delete them yourself first

---

## 6. Tagging & Releases

- Tags follow `v<major>.<minor>.<patch>` (semver)
- Tags are created from `main` only, after CI passes
- Tag message must describe what changed: `git tag -a v1.2.0 -m "Add dry-run mode for evaluation harness"`
- No force-pushing tags
