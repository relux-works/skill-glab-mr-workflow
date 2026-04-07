#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="${AGENTS_REPO_ROOT:-$(git -C "$SCRIPT_DIR/../../.." rev-parse --show-toplevel)}"
SKILL_NAME="${AGENTS_SKILL_NAME:-$(basename "$(cd "$SCRIPT_DIR/.." && pwd)")}"
PHASE="${1:-${AGENTS_HOOK_PHASE:-check}}"

case "$PHASE" in
  check|setup)
    :
    ;;
  *)
    printf 'Unknown phase: %s\n' "$PHASE" >&2
    exit 1
    ;;
esac

export AGENTS_OUTPUT_PREFIX="${AGENTS_OUTPUT_PREFIX:-[agents] Skill ${SKILL_NAME} (${PHASE})}"

"$REPO_ROOT/Scripts/agents/ensure-glab-auth.sh" "$PHASE"
