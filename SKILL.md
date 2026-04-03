---
name: skill-glab-mr-workflow
description: Use when Codex needs to work with one or more self-hosted or cloud GitLab instances through the bundled GitLab workflow wrappers, including listing my open merge requests, assigned or review-queue merge requests, macOS Keychain auth, merge request URLs or repo/iid targets, MR creation, review reads, approvals, merges, pipeline status checks, failed job trace summaries, and manual CI job execution through the bundled gmr wrapper.
triggers:
  - "glab mr"
  - "gitlab merge request"
  - "gitlab mr status"
  - "my open merge requests"
  - "show my open merge requests"
  - "merge requests assigned to me"
  - "my review queue"
  - "pipeline failed in mr"
  - "manual jobs on mr"
---

# skill-glab-mr-workflow

## Default Mode

- Execute the bundled commands yourself and return the result.
- Do not answer with a shell tutorial when the skill is already installed and authentication exists.
- Show commands only when the user explicitly asks for setup steps or when setup/auth is missing.
- Answer in the user's language unless the user explicitly asks for a different language.
- The final answer must be entirely in the user's language.
- Do not repeat an identical successful read command. Reuse the first successful result unless the context changed or the first result was incomplete.
- Before sending the final answer, do one completeness check against the original user request. If the answer is not good enough yet, keep using tools instead of finalizing.
- Resolve command paths from this skill file path.
- If the skill file path is `/abs/path/to/SKILL.md`, then:
  - `<gmr-command>` is `/abs/path/to/scripts/gmr`
  - `<bootstrap-command>` is `/abs/path/to/scripts/bootstrap-glab-keychain.sh`
  - `<ensure-command>` is `/abs/path/to/scripts/ensure-glab-auth.sh`
- Prefer those absolute command paths unless the repository bootstrap already provisioned `.agents/bin/gmr` through repo-level `make agents` and that repo-local bin layer is on `PATH`.
- Bare `gmr` is acceptable only when it resolves through that repo-local `.agents/bin` layer.
- This skill does not provision `PATH` itself. Repo-level command shims belong to the project bootstrap layer.
- Do not run `scripts/gmr` as a path relative to the current working directory.
- Prefer a full MR URL when the user provides one.
- Prefer `<gmr-command>` for agent-facing MR lists, MR status, pipeline diagnostics, failed-job root cause extraction, and manual-job operations.
- Prefer `<gmr-command>` for weak-model-safe create, approve, and merge actions.
- Prefer direct `glab` commands for rebase and note.
- When the project `AGENTS.md` defines a default GitLab host for this repository, prefer explicit commands with that host and do not enumerate other hosts first.
- For prompts like "покажи мои открытые MR", "какие у меня открытые merge requests", "show my open merge requests", "what MRs are assigned to me", or "my review queue", stay in this skill and use `<gmr-command> mr list` with `--mine` or `--mine-role` instead of a project-wide unfiltered list.
- See [`references/cli-surface.md`](references/cli-surface.md) for the one-screen command map.

## Resolve Context First

Always begin with auth verification for the actual target type:

```bash
<ensure-command> <hostname-or-url>
```

For merge request targets, use the bundled resolver instead of passing the target directly to `<ensure-command>`:

```bash
<gmr-command> auth ensure-mr <mr-target>
<gmr-command> auth ensure-mr <iid> --repo <repo> --hostname <host>
```

Choose the target context in this order:

1. If the user gives a full MR URL, use that as `<mr-target>`.
2. If the user gives only an MR IID, supply `--repo <group/subgroup/project>` and, when needed, `--hostname <host>`.
3. If the user is inside a matching git checkout, `<gmr-command>` can infer repo context from `origin`, but full MR URLs are still preferred because they are less ambiguous.

In all commands below:

- `<mr-target>` is either a full MR URL like `https://gitlab.example.com/group/project/-/merge_requests/123` or an IID like `123`
- `<repo>` is a real `GROUP/NAMESPACE/REPO` path
- `<host>` is a real GitLab hostname

Rules:

- Never pass a bare MR IID like `123` to `<ensure-command>`.
- Use `<ensure-command>` only for explicit hostnames or host URLs.
- Use `<gmr-command> auth ensure-mr ...` for anything that is an MR URL or MR IID.
- After the first successful `<gmr-command>` read, reuse the resolved `hostname`, `repo`, `iid`, and `head_pipeline.id` from that output for all raw `glab` calls. Do not re-infer them if you already have them.

If auth is missing, bootstrap it first:

```bash
<bootstrap-command> https://gitlab.example.com/
```

If several hosts are configured and the user did not specify one, inspect them with:

```bash
glab auth status --all
```

For repo-scoped GitLab workflows, choose the target host in this order:

1. Explicit MR URL or explicit hostname from the user.
2. Default GitLab host defined in the project `AGENTS.md`.
3. Host inferred from the current repository context when it is unambiguous.
4. `glab auth status --all` only as fallback discovery.
5. Ask the user only if several configured hosts look equally relevant or no relevant host exists.

Rules:

- When the project `AGENTS.md` defines a default GitLab host, pass it explicitly to `<gmr-command>` or raw `glab`.
- Do not rely on whichever host `glab` currently prefers when a repo-default host exists.
- For repo prompts like "my open merge requests" or "my review queue", prefer the repo-default host before generic host enumeration.

## Fast Path: MR Status

For prompts like:

- "какой статус у MR"
- "почему pipeline упал"
- "check this MR"
- "what failed in this merge request"

use this order:

1. Run the auth check that matches the target form:

```bash
<gmr-command> auth ensure-mr <mr-target>
<gmr-command> auth ensure-mr <iid> --repo <repo> --hostname <host>
```

2. Prefer the high-level read first:

```bash
<gmr-command> mr status <mr-target>
```

3. If the target was only an IID, use:

```bash
<gmr-command> mr status <iid> --repo <repo> --hostname <host>
```

4. If the result reports failed jobs, summarize:
   - MR state and draft status
   - head pipeline status and URL
   - each failed job name and URL
   - the extracted failure lines from the job trace
5. Only if the high-level output is incomplete, inspect the raw pipeline in GitLab:

```bash
glab ci view -R <repo> -p <pipeline-id>
```

Return the actual status and root cause. Do not stop at "pipeline failed" when the trace already contains a precise reason.

## Project MR Lists

For prompts like:

- "покажи мои открытые MR"
- "какие у меня открытые merge requests"
- "show my open merge requests"

use:

```bash
<gmr-command> mr list --repo <repo> --hostname <host> --mine
```

For prompts like:

- "что назначено мне"
- "which MRs are assigned to me"

use:

```bash
<gmr-command> mr list --repo <repo> --hostname <host> --mine --mine-role assignee
```

For prompts like:

- "что у меня на ревью"
- "my review queue"

use:

```bash
<gmr-command> mr list --repo <repo> --hostname <host> --mine --mine-role reviewer
```

Use `<gmr-command>` for project-level merge request lists:

```bash
<gmr-command> mr list --repo <repo> --hostname <host>
<gmr-command> mr list --repo <repo> --hostname <host> --state closed
<gmr-command> mr list --repo <repo> --hostname <host> --state merged
<gmr-command> mr list --repo <repo> --hostname <host> --author <username>
<gmr-command> mr list --repo <repo> --hostname <host> --assignee <username>
<gmr-command> mr list --repo <repo> --hostname <host> --reviewer <username>
<gmr-command> mr list --repo <repo> --hostname <host> --mine
<gmr-command> mr list --repo <repo> --hostname <host> --mine --mine-role assignee
```

Rules:

- `mr list` is the default path for opened/closed/merged MR lists on a project.
- Use `--state opened|closed|merged|all` instead of remembering raw `glab` flags.
- Use `--mine` to filter by the current developer.
- `--mine` defaults to author filtering.
- `--mine-role assignee` and `--mine-role reviewer` switch the target field.
- Current developer resolution for `--mine`:
  - first read repo-local `git config --local user.email`
  - then read `git config --worktree user.email` when available
  - then read effective `git config user.email`
  - then fall back to `git config --global user.email`
  - take the localpart before `@`
  - if the authenticated GitLab username matches or starts with that localpart, prefer the authenticated username
- You may also pass `--author mine`, `--assignee mine`, `--reviewer mine`, or `@me`; the wrapper resolves them to the same current user logic.
- Do not combine `--mine` with the same explicit field filter.
- Do not combine `--draft` and `--not-draft`.

## Pipeline Reads And Manual Jobs

Use `<gmr-command>` for stable MR-bound CI reads:

```bash
<gmr-command> mr status <mr-target>
<gmr-command> mr manual-jobs <mr-target>
<gmr-command> mr run-manual <job-id> --mr <mr-target>
<gmr-command> mr run-manual <job-name> --mr <mr-target>
```

Rules:

- `mr status` is the default read path for MR-bound pipeline status.
- `mr manual-jobs` lists only manual jobs from the MR head pipeline.
- `mr run-manual` is the preferred write path for manual jobs because it works from any directory and does not require an interactive TUI.
- If the user names a manual job by name and several jobs share that name, ask which one to run.
- If there is no head pipeline, say so explicitly instead of guessing.
- If there are no manual jobs, say that directly.

Use direct `glab` CI commands only when you need the raw pipeline view or non-MR pipeline operations:

```bash
glab ci list -R <repo> --source merge_request_event
glab ci view -R <repo> -p <pipeline-id>
glab ci trace <job-id> -R <repo>
glab ci retry <job-id> -R <repo>
glab ci run --mr -R <repo>
```

## Review Reads

Use `<gmr-command>` to build the review context first:

```bash
<gmr-command> mr review-context <mr-target>
<gmr-command> mr review-context <mr-target> --include-bots
```

Then inspect the MR itself:

```bash
glab mr view <iid> -R <repo> --comments --unresolved
glab mr diff <iid> -R <repo> --raw
```

Rules:

- Start with `review-context`, not with the raw diff.
- Reuse the already resolved `iid`, `repo`, and `hostname` from `review-context` or `mr status` for every following raw `glab` call.
- Review context must cover:
  - MR title, state, draft flag, merge status, source branch, target branch
  - head pipeline status
  - unresolved discussions
  - changed file list
- `review-context` filters bot-generated discussion noise by default.
- Re-run with `--include-bots` only when the user explicitly wants bot discussions too.
- If the pipeline is red, mention that before style or naming comments.
- Prefer `glab mr diff --raw` when you need to reason over the actual patch.
- Prefer `glab mr view --comments --unresolved` when review threads matter.
- Use `glab mr note` for new review comments.
- Use `glab mr note resolve` and `glab mr note reopen` only when the user explicitly asks to change discussion state.

When the user asks for a review, findings come first. Follow the normal code-review contract:

- prioritize bugs, regressions, risky assumptions, missing tests, and unresolved blockers
- cite concrete files, jobs, or discussion items when possible
- keep summaries brief and secondary to findings

See [`references/review-checklist.md`](references/review-checklist.md) for the compact review order.

## MR Mutations

Use the high-level write surface when possible:

```bash
<gmr-command> mr create --fill
<gmr-command> mr create --title '<title>' --description '<description>'
<gmr-command> mr create --repo <repo> --hostname <host> --source-branch <source-branch> --target-branch <target-branch> --title '<title>' --description '<description>'
<gmr-command> mr create --fill --draft
<gmr-command> mr approve <mr-target>
<gmr-command> mr approve <mr-target> --sha <head-sha>
<gmr-command> mr merge <mr-target>
<gmr-command> mr merge <mr-target> --auto-merge
<gmr-command> mr merge <mr-target> --keep-source-branch
```

Use direct `glab mr` commands for the remaining writes:

```bash
glab mr rebase <iid> -R <repo>
glab mr note <iid> -R <repo> -m '<comment>'
```

Rules:

- Prefer `gmr mr create` over raw `glab mr create` for weak-model-safe writes.
- `gmr mr create` is non-interactive. Use `--fill` or provide `--title`. If the source branch cannot be inferred from the current checkout, pass `--source-branch`.
- Prefer `gmr mr approve` and `gmr mr merge` over raw `glab` for weak-model-safe writes.
- Prefer `--sha <head-sha>` on `approve` and `merge` when acting on a reviewed commit.
- Do not approve or merge unless the user explicitly asks for that write action.
- `gmr mr merge` refuses draft MRs.
- `gmr mr merge` refuses failed head pipelines and requires `--auto-merge` if the head pipeline is still running.
- If the user asks to create an MR and the branch and repo are already obvious, `gmr mr create --fill` is the fast path.
- If the title, description, target branch, labels, reviewers, or draft state must be explicit, pass them directly instead of opening the browser.
- If merge depends on a green pipeline and the pipeline is red, say so before executing the merge.

## Ask Only If Blocked

Ask the user only when one of these is true:

- no GitLab auth exists for the target host
- the user provided only an IID and neither `--repo` nor an inferable git checkout is available
- several hosts are configured and the target host is ambiguous
- a manual job name matches several jobs
- a destructive or write action was not explicitly requested

Otherwise, run the commands and return the result.

## Output Contract

When answering a project MR list query:

- include every matching MR iid, title, state, draft flag, source branch, target branch, and updated_at when the payload provides it
- include `total`/`count` from the tool payload when available
- include the full raw MR URL for every listed MR when the tool payload provides it

When answering an MR status query:

- include MR title and URL
- include `state`, `draft`, and `detailed_merge_status`
- include the head pipeline status, pipeline id, and pipeline URL
- list every failed non-allowed-failure job with job id, name, stage, and URL
- include the extracted failure lines for each failed job when available
- include manual jobs when they exist
- write the final answer in the user's language

When answering a review query:

- findings first
- include pipeline blockers before code-style issues
- mention unresolved discussion count when relevant
- include changed files or affected areas when that helps explain the findings

When answering a manual-job query:

- include pipeline id
- include every manual job id, name, stage, and URL
- state explicitly which job was triggered if the user asked to run one

## Pre-final Check

Before sending the final answer:

1. Draft the answer from the tool results you already have.
2. Compare that draft against the original user request.
3. Ask these questions:
   - Does the draft answer the user's actual question directly?
   - If the user gave a specific MR URL, does the answer refer to that exact MR?
   - If the pipeline failed, did the answer include the real failure cause rather than only the top-level status?
   - If the user asked for a review, are findings first?
   - Is every non-literal part of the final answer written in the user's language?
4. If any answer is "no", continue with the next needed tool call instead of finalizing.
5. If all answers are "yes", send that draft as the final answer.

Do this once per response. Do not loop on repeated self-checks after you already have a good direct answer.

## Setup Fallback

Use this only when installation or authentication is missing.

Install into one repository from the source skill repo:

```bash
make install REPO=/abs/path/to/repo LOCALE=<locale>
```

Bootstrap the committed repo-local runtime after clone or when a project bootstrap script refreshes the tracked runtime:

```bash
make -C <repo>/.agents/skills/skill-glab-mr-workflow skill
```

Install:

```bash
brew install glab
```

Bootstrap Keychain-backed auth:

```bash
<bootstrap-command> https://gitlab.example.com/
```

Verify auth:

```bash
<ensure-command> https://gitlab.example.com/
glab auth status --hostname gitlab.example.com
```

## Safety Rules

- Keep GitLab tokens in macOS Keychain through `glab auth login --use-keyring`.
- Do not save GitLab tokens in shell history, env files, or checked-in files.
- Do not use `glab auth status --show-token` unless the user explicitly asks to reveal the token.
- Prefer full MR URLs because they remove host and repo ambiguity.
- Treat `approve`, `merge`, `rebase`, `note resolve`, and manual-job execution as write actions that require explicit user intent.
- Prefer `--sha` guards on approve and merge when the exact reviewed commit matters.
