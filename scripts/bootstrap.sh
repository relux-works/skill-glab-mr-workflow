#!/usr/bin/env bash
set -euo pipefail

quiet=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet)
      quiet=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 1
}

if [[ $quiet -eq 0 ]]; then
  echo "skill-glab-mr-workflow ready"
fi
