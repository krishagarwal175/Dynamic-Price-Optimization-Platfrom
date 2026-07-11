# Docs — Repository-facing documentation

This folder holds documentation that belongs **with the code** for anyone who clones the
repository. It is a curated, committed subset of the wider engineering memory.

> The **source of truth** for architecture, decisions, and history is the `vault4/`
> Obsidian vault. `docs/` mirrors only the stable, repo-relevant artifacts.

| Directory | Contents | Relationship to the vault |
|-----------|----------|---------------------------|
| `architecture/` | Rendered, stable architecture references for contributors. | Distilled from `vault4/02-Architecture/`. |
| `adr/` | Committed mirror of **accepted** Architecture Decision Records. | Copied from `vault4/04-Decisions-ADR/` once an ADR is accepted. |
| `diagrams/` | Exported diagram images and source files. | Assets referenced by both docs and vault. |

## Update rule

`docs/adr/` receives a copy of an ADR only when that ADR reaches **Accepted** status in
the vault. Draft and proposed ADRs stay in the vault until accepted.
