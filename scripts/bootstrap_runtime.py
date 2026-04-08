#!/usr/bin/env python3
"""Skill-local bootstrap: verify runtime dependencies and report readiness."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SKILL_NAME = "skill-glab-mr-workflow"
MANIFEST_FILENAME = ".skill-install.json"
DEPENDENCIES_FILENAME = "dependencies.json"


def detect_language(skill_dir: Path) -> str:
    manifest_path = skill_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return "en"
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "en"
    locale = payload.get("primary_locale") or payload.get("locale_mode") or "en"
    if isinstance(locale, str):
        normalized = locale.strip().lower()
        if normalized:
            return normalized.split("-", 1)[0].split("_", 1)[0]
    return "en"


def warn_missing_dependencies(skill_dir: Path, language: str) -> None:
    deps_path = skill_dir / DEPENDENCIES_FILENAME
    if not deps_path.exists():
        return
    try:
        payload = json.loads(deps_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    dependencies = payload.get("dependencies")
    if not isinstance(dependencies, list):
        return
    for dep in dependencies:
        if not isinstance(dep, dict):
            continue
        command = dep.get("command")
        install = dep.get("install")
        if not isinstance(command, str) or not command.strip():
            continue
        if shutil.which(command):
            continue
        hint = install.strip() if isinstance(install, str) and install.strip() else "see repository dependencies.json"
        if language == "ru":
            print(
                f"Отсутствует системная зависимость {command}. "
                f"Установите её перед использованием скилла: {hint}",
                file=sys.stderr,
            )
        else:
            print(
                f"Missing machine dependency {command}. "
                f"Install it before using the skill: {hint}",
                file=sys.stderr,
            )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=f"Bootstrap {SKILL_NAME} runtime.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    skill_dir = Path(__file__).resolve().parent.parent
    language = detect_language(skill_dir)
    warn_missing_dependencies(skill_dir, language)

    if not args.quiet:
        print(f"{SKILL_NAME} ready")


if __name__ == "__main__":
    main()
