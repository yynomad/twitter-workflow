#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--status" ]]; then
  git rev-parse --abbrev-ref HEAD
  git status --short
  exit 0
fi

branch="$(git rev-parse --abbrev-ref HEAD)"
echo "[preflight] branch: ${branch}"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "[preflight] working tree is dirty; commit/stash first." >&2
  exit 2
fi

echo "[preflight] fetching origin..."
git fetch origin --prune

echo "[preflight] rebasing from origin/${branch}..."
git pull --rebase origin "${branch}"

echo "[preflight] sync complete."
