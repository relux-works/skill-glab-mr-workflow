# skill-glab-mr-workflow

GitLab merge request workflow skill for Codex and Claude Code, built around local `glab` commands and the bundled `gmr` wrapper. It covers both MR status/review work and natural requests like "show my open merge requests" or "what is assigned to me".

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
- `setup.sh`: repo-level convenience wrapper around the bundled installer
- `scripts/setup.sh`, `scripts/setup_main.py`, `scripts/setup_support.py`: vendored standalone skill install helper
- `scripts/gmr`: high-level MR workflow wrapper
- `scripts/bootstrap-glab-keychain.sh`: initial auth bootstrap
- `scripts/ensure-glab-auth.sh`: auth preflight
- `references/`: compact command and review references
- `tests/`: unit tests for the wrapper logic

## Install

Install the skill through the managed setup flow instead of symlinking the
source checkout directly:

```bash
./setup.sh global --locale ru-en
```

This creates a managed runtime copy under
`${XDG_DATA_HOME:-~/.local/share}/agents/skills/skill-glab-mr-workflow` and
points `~/.claude/skills/skill-glab-mr-workflow` and
`~/.codex/skills/skill-glab-mr-workflow` at that installed copy.

On global installs, the shared helper also registers the skill triggers in
`~/.agents/.instructions/INSTRUCTIONS_SKILL_TRIGGERS.md`.

For a project-local install:

```bash
./setup.sh local /abs/path/to/repo --locale ru-en
```

This creates `<repo>/.skills/skill-glab-mr-workflow` and rewires the
project-local `.claude/skills` and `.codex/skills` links to that copy.

On local installs, the shared helper also provisions
`.agents/.instructions/INSTRUCTIONS_TESTING.md` in the target repo and ensures
the repo root `AGENTS.md` references it from the `Modules` section.

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

Localization is part of the shared install helper, not a separate repo-local
install path. This repo only supplies locale data in `locales/metadata.json`;
the helper renders the installed `SKILL.md` and `agents/openai.yaml` for the
selected locale and keeps global/local infra wiring consistent.

## License

MIT. See [LICENSE](LICENSE).
