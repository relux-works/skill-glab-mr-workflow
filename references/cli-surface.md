# CLI Surface

Use this file as the fastest command chooser for weak models. Prefer the left-to-right mapping. Reuse already resolved `hostname`, `repo`, `iid`, and `pipeline id` instead of re-inferring them.

| Goal | Preferred command | Notes |
| --- | --- | --- |
| Verify auth for host | `<ensure-command> <hostname-or-url>` | Use only for a real host or host URL. |
| Verify auth for MR target | `<gmr-command> auth ensure-mr <mr-target>` | Use for MR URL or IID. |
| List opened MRs on project | `<gmr-command> mr list --repo <repo> --hostname <host>` | Default state is `opened`. |
| List closed or merged MRs | `<gmr-command> mr list --repo <repo> --hostname <host> --state closed|merged|all` | Prefer `--state` over raw `glab` flags. |
| List my MRs | `<gmr-command> mr list --repo <repo> --hostname <host> --mine` | Default `--mine` role is `author`. |
| List MRs assigned to me | `<gmr-command> mr list --repo <repo> --hostname <host> --mine --mine-role assignee` | Uses current developer resolution. |
| List MRs waiting for my review | `<gmr-command> mr list --repo <repo> --hostname <host> --mine --mine-role reviewer` | Use for prompts like "my review queue". |
| List MRs by explicit user | `<gmr-command> mr list --repo <repo> --hostname <host> --author <user>` | Also supports `mine`, `me`, `@me`. |
| Check MR status | `<gmr-command> mr status <mr-target>` | Default read path for MR-bound pipeline status. |
| List manual jobs on MR pipeline | `<gmr-command> mr manual-jobs <mr-target>` | Returns only `manual` jobs from head pipeline. |
| Run a manual job | `<gmr-command> mr run-manual <job-id-or-name> --mr <mr-target>` | If name is ambiguous, stop and ask. |
| Build review context | `<gmr-command> mr review-context <mr-target>` | Filters bot noise by default. |
| Build review context with bots | `<gmr-command> mr review-context <mr-target> --include-bots` | Use only when bot notes matter. |
| Create MR from current branch with generic fill | `<gmr-command> mr create --fill` | Convenience path only when the repository has no repo-local title, description, or checklist policy. Post-read the created MR afterwards. |
| Create MR with explicit policy-driven fields | `<gmr-command> mr create --title '<title>' --description '<description>'` | Default mode when repo-local conventions exist. Add `--target-branch`, `--draft`, `--label`, `--reviewer`, `--assignee` as needed, then validate the created MR after the write. |
| Approve MR | `<gmr-command> mr approve <mr-target>` | Uses resolved head SHA automatically unless overridden. |
| Merge MR | `<gmr-command> mr merge <mr-target>` | Refuses draft or failed head pipeline. |
| Merge while pipeline is still running | `<gmr-command> mr merge <mr-target> --auto-merge` | Use only when user explicitly wants auto-merge. |
| Rebase MR | `glab mr rebase <iid> -R <repo>` | Reuse resolved repo/iid/hostname. |
| Add MR comment | `glab mr note <iid> -R <repo> -m '<comment>'` | Reuse resolved repo/iid/hostname. |
| Inspect raw MR discussions | `glab mr view <iid> -R <repo> --comments --unresolved` | Use after `review-context`. |
| Inspect raw MR diff | `glab mr diff <iid> -R <repo> --raw` | Use after `review-context`. |
| Inspect raw pipeline | `glab ci view -R <repo> -p <pipeline-id>` | Use only if `mr status` was incomplete. |
| Trace a failed job | `glab ci trace <job-id> -R <repo>` | Usually not needed if `mr status` already extracted the failure cause. |
| Retry a failed job | `glab ci retry <job-id> -R <repo>` | Write action. Only on explicit user intent. |

## Defaults

- Prefer full MR URLs.
- Prefer `gmr` over raw `glab` whenever both can do the job.
- Prefer non-interactive commands.
- Prefer resolved context over re-detecting context.
- If repo-local MR conventions exist, default to explicit `title` and `description` instead of `--fill`.
- Always re-read the created MR after `mr create` and let the calling layer validate repo-local policy.
- `--mine` resolves the current developer from git email plus authenticated GitLab username.
- For prompts like "мои открытые MR" or "my open merge requests", prefer `mr list --mine`.
