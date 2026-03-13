---
name: git-sync-before-edit
description: Enforce a pre-edit git sync workflow (fetch, pull --rebase, conflict handling) before making any code changes in an existing repository.
---

# Git Sync Before Edit

Use this skill whenever the user asks to modify code in a git repository and wants to reduce branch drift.

## Workflow

1. Confirm current branch and working tree status.
2. Run `scripts/preflight_sync.sh`.
3. If rebase conflicts occur:
   - stop code edits;
   - resolve conflicts;
   - continue or abort rebase;
   - re-run preflight sync.
4. Only after sync succeeds, proceed with code changes.

## Commands

- Status only: `bash scripts/preflight_sync.sh --status`
- Full sync: `bash scripts/preflight_sync.sh`

## Rules

- Never run `git pull` with merge strategy unless user explicitly asks.
- Do not auto-stash or discard local changes.
- If working tree is dirty, ask/decide with user workflow before pulling.
