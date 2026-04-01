# skill-glab-mr-workflow

GitLab merge request workflow skill for Codex and Claude Code, built around local `glab` commands and the bundled `gmr` wrapper.

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
- `scripts/gmr`: high-level MR workflow wrapper
- `scripts/bootstrap-glab-keychain.sh`: initial auth bootstrap
- `scripts/ensure-glab-auth.sh`: auth preflight
- `references/`: compact command and review references
- `tests/`: unit tests for the wrapper logic

## Install

Symlink this repo into the skill directories used by your agent runtimes:

```bash
ln -sfn /absolute/path/to/skill-glab-mr-workflow ~/.codex/skills/skill-glab-mr-workflow
ln -sfn /absolute/path/to/skill-glab-mr-workflow ~/.claude/skills/skill-glab-mr-workflow
```

## Quick Start

```bash
scripts/bootstrap-glab-keychain.sh https://gitlab.example.com/
scripts/gmr mr status https://gitlab.example.com/group/project/-/merge_requests/123
scripts/gmr mr review-context https://gitlab.example.com/group/project/-/merge_requests/123
scripts/gmr mr list --repo group/project --hostname gitlab.example.com --mine
scripts/gmr mr create --fill
scripts/gmr mr approve https://gitlab.example.com/group/project/-/merge_requests/123
scripts/gmr mr merge https://gitlab.example.com/group/project/-/merge_requests/123
```

## License

MIT. See [LICENSE](LICENSE).
