Switch to main, sync with remote, and review GitHub issue statuses.

## Step 1 — Switch to main and fetch remote

```bash
git checkout main && git pull origin main
```

## Step 2 — Fetch all open issues

```bash
gh issue list --state open --limit 100
```

Also fetch recently closed issues to check for anything that was missed:

```bash
gh issue list --state closed --limit 20
```

## Step 3 — Cross-reference issues against the codebase

For each open issue, reason about its status:

- **Should be closed:** the work is done and merged to main (check git log, Lambda files, Terraform files, and test files for evidence)
- **Should be marked in-progress:** work has started on a branch or PR is open
- **Blocked or stale:** depends on another issue that isn't done yet — note the dependency
- **Still genuinely open:** no work started, not blocked

Use `gh pr list --state merged` and `git log --oneline -30` to help correlate merged PRs with issue numbers.

## Step 4 — Present a triage summary

Output a table like this:

| # | Title | Current label | Suggestion | Reason |
|---|-------|--------------|------------|--------|
| 31 | Implement submitAnswer Lambda | in-progress | Close | Merged in PR #64 |
| 66 | Replace feedback_every_n | in-progress | Close | Merged in PR #70 |

Then ask the user which updates to apply.

## Step 5 — Apply confirmed updates

For each issue the user confirms:
- Close with: `gh issue close <number> --comment "<one sentence why>"`
- Update label with: `gh issue edit <number> --add-label "<label>" --remove-label "<label>"`

Only apply what the user explicitly confirms.
