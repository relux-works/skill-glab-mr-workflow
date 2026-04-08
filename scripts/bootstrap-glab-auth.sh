#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: bootstrap-glab-auth.sh <hostname-or-url>

Stores a GitLab PAT in the OS keyring through glab's built-in keyring support.

Optional environment variables:
  GITLAB_GIT_PROTOCOL   Defaults to: ssh
  GITLAB_API_HOST       Custom API host or host:port
  GITLAB_API_PROTOCOL   Custom API protocol, for example: https
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

git_protocol="${GITLAB_GIT_PROTOCOL:-ssh}"
api_host="${GITLAB_API_HOST:-}"
api_protocol="${GITLAB_API_PROTOCOL:-}"

scheme=''
if [[ "$target" =~ ^([A-Za-z][A-Za-z0-9+.-]*)://(.+)$ ]]; then
  scheme="${BASH_REMATCH[1]}"
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
  if [[ -z "$api_host" ]]; then
    api_host="$target"
  fi
fi

if [[ -n "$scheme" && -z "$api_protocol" ]]; then
  api_protocol="$scheme"
fi

token=''
if [[ -t 0 ]]; then
  printf 'GitLab PAT for %s: ' "$hostname" >&2
  read -r -s token
  printf '\n' >&2
else
  token="$(cat)"
fi

if [[ -z "$token" ]]; then
  printf 'No token provided on stdin or prompt.\n' >&2
  exit 1
fi

args=(
  auth
  login
  --hostname "$hostname"
  --git-protocol "$git_protocol"
  --use-keyring
  --stdin
)

if [[ -n "$api_host" ]]; then
  args+=(--api-host "$api_host")
fi

if [[ -n "$api_protocol" ]]; then
  args+=(--api-protocol "$api_protocol")
fi

printf '%s' "$token" | glab "${args[@]}"
unset token

glab auth status --hostname "$hostname"
