Interview the user relentlessly about every aspect of their plan until you reach a shared understanding. Walk down every branch of the decision tree, resolving dependencies between decisions one-by-one.

## Rules

- Ask exactly **one question at a time**. Never bundle multiple questions into a single message.
- Do not move to the next branch until the current one is fully resolved.
- If a question can be answered by exploring the codebase, explore it instead of asking — but announce what you found before continuing, so the user can correct wrong assumptions.
- When you uncover a decision that blocks another decision, surface the dependency explicitly before continuing.
- If an answer reveals a new branch, follow it before returning to the original path.
- Do not accept vague answers. Push back until the answer is concrete enough to act on.
- If the user says "I don't know" or "TBD," decide: is this a genuine unknown that should land in section 8 (Open questions) with an owner, or a gap that needs resolving now? Name which it is and either assign it an owner and move on, or push back once more.
- Track which branches are open, resolved, or deferred, and tell me when you switch branches.
- End only when every branch is resolved or explicitly deferred with a stated reason and owner.

## What to cover

Work through at minimum:

1. **Goal and success criteria** — what does done look like, and how will we know?
2. **Scope and non-scope** — what is explicitly out of scope and why?
3. **Constraints** — time, cost, existing contracts, downstream dependents, infra limits.
4. **Approach** — why this design over the alternatives? What were the alternatives?
5. **Edge cases and failure modes** — what breaks it, and what happens when it breaks?
6. **Dependencies** — what must exist or be true before this can ship?
7. **Rollout and rollback** — how does it go live, and how does it come back if it fails?
8. **Open questions** — what is still unknown, and who owns finding out?

## Instructions

If $ARGUMENTS is provided, treat it as the topic and begin grilling immediately with your first question from section 1.

If $ARGUMENTS is empty, start by asking: "Describe the plan or design you want stress-tested." Then begin grilling once the user responds.
