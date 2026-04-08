<!--
Agent note: This README is a general description of the skill project for maintainers,
contributors, and evaluators. It covers architecture, packaging, and technical details.
Do not use README as operational instructions; use `SKILL.md`.
-->

# skill-glab-mr-workflow

GitLab merge request workflow skill for Codex and Claude Code, built around the bundled `gmr` wrapper and explicit GitLab auth helpers. It covers both MR status/review work and natural requests like "show my open merge requests" or "what is assigned to me".

## What It Covers

- `glab auth login --use-keyring` based auth bootstrap for GitLab.com and self-hosted GitLab
- MR status reads with pipeline and failed job summaries
- MR review context, unresolved discussions, and diff-oriented review flow
- Manual pipeline job discovery and execution
- MR create, approve, and merge wrappers
- Project MR lists with author/assignee/reviewer filters and `--mine`

## Layout

- `SKILL.md`: skill instructions and workflow
- `agents/openai.yaml`: UI metadata
- `locales/metadata.json`: install-time localized metadata excluding trigger phrases
- `.skill_triggers`: localized markdown trigger catalogs copied into runtime and treated as the single source of truth for skill triggers
- `dependencies.json`: declared machine-level command dependencies required before install
- `Makefile`: public entrypoints for `make install` in the source repo and `make skill` in a committed runtime copy
- `scripts/setup_main.py`, `scripts/setup_support.py`: source-install helper for repo-local copies, metadata rendering, and runtime packaging
- `scripts/bootstrap_runtime.py`: skill-local bootstrap entrypoint for committed runtime copies
- `scripts/make-agents.sh`: `make agents` hook entrypoint for repo-level `check`/`setup` phases
- `scripts/gmr`: MR workflow wrapper entry point (bash shim for macOS/Linux)
- `scripts/gmr.cmd`: MR workflow wrapper entry point (Windows)
- `scripts/gmr_main.py`: core MR workflow logic, auth ensure, and auth bootstrap
- `references/`: compact command and review references
- `tests/`: unit tests for the wrapper logic

## Prerequisites

- **Python 3** (3.10+)
- **glab** (GitLab CLI) — [install instructions](https://gitlab.com/gitlab-org/cli#installation)

### Installing glab

| Platform | Command |
|----------|---------|
| macOS | `brew install glab` |
| Linux (Homebrew) | `brew install glab` |
| Linux (apt, Debian/Ubuntu) | see [gitlab.com/gitlab-org/cli](https://gitlab.com/gitlab-org/cli#installation) |
| Windows (winget) | `winget install glab` |
| Windows (scoop) | `scoop install glab` |

### OS keyring for token storage

`glab auth login --use-keyring` stores tokens in the platform's native secure storage:

| Platform | Backend |
|----------|---------|
| macOS | Keychain |
| Linux | Secret Service (GNOME Keyring, KWallet) |
| Windows | Windows Credential Manager |

On headless Linux environments (CI runners, containers) Secret Service may not be available. In that case glab falls back to its config file (`~/.config/glab-cli/config.yml`).

## Install

Install the skill into one repository-local agent runtime from the source repo.

**macOS / Linux:**

```bash
make install REPO=/abs/path/to/repo LOCALE=ru-en
```

**Windows (or any platform without make):**

```
py -3 scripts/setup_main.py /abs/path/to/repo --locale ru-en
```

This creates `<repo>/.agents/skills/skill-glab-mr-workflow`, strips nested git metadata, renders installed metadata in the selected locale, and prunes installer-only files from the committed runtime copy.

Before copying anything into the target repository, install validates the declared machine-level command dependencies from `dependencies.json` and requires them to be available in `PATH`.

If any required command is missing, install fails and the runtime copy is not updated.

Install is intentionally not the place where project bootstrap policy is enforced. It installs the committed runtime copy of this skill into a repository. Whether the target repository also needs a repo-level bootstrap step such as `make agents` is project-specific and stays the responsibility of that repository.

Once the committed runtime copy already exists inside the repository, bootstrap only the skill-local runtime:

**macOS / Linux:**

```bash
make -C <repo>/.agents/skills/skill-glab-mr-workflow skill
```

**Windows:**

```
py -3 <repo>\.agents\skills\skill-glab-mr-workflow\scripts\bootstrap_runtime.py
```

Repository-level wiring such as `.claude/skills/*`, `.agents/bin/*`, and shared `PATH` setup belongs to the project bootstrap layer, not to this skill.

In other words:

- install copies and localizes the skill into one repository
- skill bootstrap verifies only that installed skill runtime
- any repository-wide bootstrap remains optional and project-defined

## Quick Start

### Auth bootstrap

Set up GitLab authentication with OS keyring storage:

**macOS / Linux:**

```bash
scripts/gmr auth bootstrap https://gitlab.example.com/
```

**Windows:**

```
scripts\gmr.cmd auth bootstrap https://gitlab.example.com/
```

### Usage examples

All `gmr` commands work identically across platforms. Use `scripts/gmr` on macOS/Linux or `scripts\gmr.cmd` on Windows.

```
gmr mr status https://gitlab.example.com/group/project/-/merge_requests/123
gmr mr review-context https://gitlab.example.com/group/project/-/merge_requests/123
gmr mr list --repo group/project --hostname gitlab.example.com --mine
gmr mr list --repo group/project --hostname gitlab.example.com --mine --mine-role assignee
gmr mr create --fill
gmr mr approve https://gitlab.example.com/group/project/-/merge_requests/123
gmr mr merge https://gitlab.example.com/group/project/-/merge_requests/123
```

On any platform, `python3 scripts/gmr_main.py <args>` (or `py -3 scripts/gmr_main.py <args>` on Windows) is always a valid alternative to the platform-specific shims.

## Localization

Localization is part of the source install helper. This repo supplies localized UI metadata in `locales/metadata.json` and localized trigger catalogs in `.skill_triggers/*.md`; install renders the installed `SKILL.md` and `agents/openai.yaml` for the selected locale and produces a committed-safe runtime copy for the target repository.
