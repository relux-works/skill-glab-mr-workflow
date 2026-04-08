#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: ensure-glab-auth.sh <hostname-or-url>

Checks that glab has a working authentication record for the given GitLab hostname.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

target="${1:-}"
if [[ -z "$target" ]]; then
  usage
  exit 1
fi

if ! command -v glab >/dev/null 2>&1; then
  printf 'glab is not installed or not in PATH.\n' >&2
  exit 1
fi

if [[ "$target" =~ ^([A-Za-z][A-Za-z0-9+.-]*)://(.+)$ ]]; then
  target="${BASH_REMATCH[2]}"
fi

target="${target%%/*}"
target="${target##*@}"

if [[ -z "$target" ]]; then
  printf 'Could not parse a hostname from input.\n' >&2
  exit 1
fi

hostname="$target"
if [[ "$target" == *:* ]]; then
  hostname="${target%%:*}"
fi

if glab auth status --hostname "$hostname" >/dev/null 2>&1; then
  printf 'glab authentication is configured for %s.\n' "$hostname" >&2
  exit 0
fi

printf 'glab authentication is missing for %s.\n' "$hostname" >&2
printf 'Bootstrap it with: scripts/bootstrap-glab-auth.sh %s\n' "$hostname" >&2
exit 1
