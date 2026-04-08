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

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST_PATH="$SKILL_DIR/.skill-install.json"
DEPENDENCIES_PATH="$SKILL_DIR/dependencies.json"

detect_language() {
  if [[ -f "$MANIFEST_PATH" ]]; then
    python3 - "$MANIFEST_PATH" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
except Exception:
    print("en")
    raise SystemExit

locale = payload.get("primary_locale") or payload.get("locale_mode") or "en"
if isinstance(locale, str):
    normalized = locale.strip().lower()
    if normalized:
        print(normalized.split("-", 1)[0].split("_", 1)[0])
        raise SystemExit

print("en")
PY
    return
  fi
  echo "en"
}

warn_missing_dependencies() {
  local language="$1"

  [[ -f "$DEPENDENCIES_PATH" ]] || return 0

  python3 - "$DEPENDENCIES_PATH" "$language" <<'PY'
import json
import shutil
import sys

path = sys.argv[1]
language = sys.argv[2]

try:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
except Exception:
    raise SystemExit(0)

dependencies = payload.get("dependencies")
if not isinstance(dependencies, list):
    raise SystemExit(0)

for dependency in dependencies:
    if not isinstance(dependency, dict):
        continue
    command = dependency.get("command")
    install = dependency.get("install")
    if not isinstance(command, str) or not command.strip():
        continue
    if shutil.which(command):
        continue
    install_hint = install.strip() if isinstance(install, str) and install.strip() else "see repository dependencies.json"
    if language == "ru":
        print(
            f"Отсутствует системная зависимость {command}. "
            f"Установите её перед использованием скилла: {install_hint}",
            file=sys.stderr,
        )
    else:
        print(
            f"Missing machine dependency {command}. "
            f"Install it before using the skill: {install_hint}",
            file=sys.stderr,
        )
PY
}

language="$(detect_language)"
warn_missing_dependencies "$language"

if [[ $quiet -eq 0 ]]; then
  echo "skill-glab-mr-workflow ready"
fi
