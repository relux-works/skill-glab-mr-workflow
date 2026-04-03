<!--
Agent note: This README is a general description of the skill project for maintainers,
contributors, and evaluators. It covers architecture, packaging, and technical details.
Do not use README as operational instructions; use `SKILL.md`.
-->

# skill-glab-mr-workflow

GitLab merge request workflow skill for Codex and Claude Code, built around the bundled `gmr` wrapper and explicit GitLab auth helpers. It covers both MR status/review work and natural requests like "show my open merge requests" or "what is assigned to me".

## What It Covers

- macOS Keychain-backed `glab` auth for GitLab.com and self-hosted GitLab
- MR status reads with pipeline and failed job summaries
- MR review context, unresolved discussions, and diff-oriented review flow
- Manual pipeline job discovery and execution
- MR create, approve, and merge wrappers
- Project MR lists with author/assignee/reviewer filters and `--mine`

## Layout

- `SKILL.md`: skill instructions and workflow
- `agents/openai.yaml`: UI metadata
- `locales/metadata.json`: install-time localized metadata and trigger catalog
- `Makefile`: public entrypoints for `make install` in the source repo and `make skill` in a committed runtime copy
- `scripts/setup_main.py`, `scripts/setup_support.py`: source-install helper for repo-local copies, metadata rendering, and runtime packaging
- `scripts/bootstrap.sh`: skill-local bootstrap entrypoint for committed runtime copies
- `scripts/gmr`: high-level MR workflow wrapper
- `scripts/bootstrap-glab-keychain.sh`: initial auth bootstrap
- `scripts/ensure-glab-auth.sh`: auth preflight
- `references/`: compact command and review references
- `tests/`: unit tests for the wrapper logic

## Install

Install the skill into one repository-local agent runtime from the source repo:

```bash
make install REPO=/abs/path/to/repo LOCALE=ru-en
```

This creates `<repo>/.agents/skills/skill-glab-mr-workflow`, strips nested git
metadata, renders installed metadata in the selected locale, and prunes
installer-only files from the committed runtime copy.

Once the committed runtime copy already exists inside the repository, bootstrap
only the skill-local runtime with:

```bash
make -C <repo>/.agents/skills/skill-glab-mr-workflow skill
```

Repository-level wiring such as `.claude/skills/*`, `.agents/bin/*`, and shared
`PATH` setup belongs to the project bootstrap layer, not to this skill.

## Quick Start

```bash
scripts/bootstrap-glab-keychain.sh https://gitlab.example.com/
scripts/gmr mr status https://gitlab.example.com/group/project/-/merge_requests/123
scripts/gmr mr review-context https://gitlab.example.com/group/project/-/merge_requests/123
scripts/gmr mr list --repo group/project --hostname gitlab.example.com --mine
scripts/gmr mr list --repo group/project --hostname gitlab.example.com --mine --mine-role assignee
scripts/gmr mr create --fill
scripts/gmr mr approve https://gitlab.example.com/group/project/-/merge_requests/123
scripts/gmr mr merge https://gitlab.example.com/group/project/-/merge_requests/123
```

Localization is part of the source install helper. This repo supplies locale
data in `locales/metadata.json`; `make install` renders the installed `SKILL.md`
and `agents/openai.yaml` for the selected locale and produces a committed-safe
runtime copy for the target repository.

## License

MIT. See [LICENSE](LICENSE).
