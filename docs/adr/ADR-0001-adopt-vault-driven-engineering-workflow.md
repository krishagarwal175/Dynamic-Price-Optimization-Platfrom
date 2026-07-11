# ADR-0001: Adopt a vault-driven, documentation-first engineering workflow

- **Status:** Accepted
- **Date:** 2026-07-11
- **Deciders:** Krish Agarwal
- **Related:** [[documentation_standards]], [[development_workflow]], [[definition_of_done]]

## Context

The project must guarantee that **no architectural decision or implementation detail is
ever lost**, while remaining professional and not overengineered. It also serves as an
interview and learning artifact, so the *reasoning* behind the system matters as much as
the code. A separate Obsidian vault (`vault4/`) is designated as permanent engineering
memory, kept local and outside version control.

## Decision

We will run a **documentation-first workflow** in which the `vault4/` Obsidian vault is a
first-class deliverable. Every feature follows a fixed pipeline (see
[[development_workflow]]) and is only "done" when it satisfies a strict
[[definition_of_done]] that includes vault synchronization. The code repository is
versioned on GitHub; the vault is maintained locally and **excluded from Git** by
explicit instruction.

## Options considered

1. **Code-only, docs as afterthought** — fastest short term; loses rationale and
   history, poor interview value. Rejected.
2. **Docs inside the repo (`/docs` only)** — versioned with code, but heavier and less
   navigable than an Obsidian vault; mixes long-form memory with shipping code.
   Partially adopted: `docs/` holds a *mirror* of stable artifacts.
3. **Separate Obsidian vault as engineering memory (chosen)** — rich linking, clear
   separation of memory from code, excellent for reasoning and interview prep.

## Consequences

- **Positive:** durable rationale; a single navigable history; strong interview value;
  clear operating contract for every change.
- **Negative / trade-offs:** the vault can drift if discipline lapses — mitigated by
  making sync part of the Definition of Done. The vault is not backed up by Git, so it
  relies on local/OneDrive storage.
- **Follow-ups:** maintain `docs/adr/` as the committed mirror of accepted ADRs.

## Notes

Repository name on the remote is intentionally spelled `Dynamic-Price-Optimization-Platfrom`.
