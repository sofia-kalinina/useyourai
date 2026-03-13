Full workflow: branch → commit(s) → push → PR.

## Step 1 — Understand current state

Run in parallel:
- `git status` — what's changed and what's untracked
- `git diff` — full diff of unstaged changes
- `git diff --cached` — full diff of staged changes
- `git log main..HEAD --oneline` — commits already on this branch (if any)

## Step 2 — Create branch (if not already on a feature/fix branch)

If currently on `main` or another base branch, ask the user for a branch name or propose one based on the changes.
Branch naming: `feature/<kebab-case-description>` or `fix/<kebab-case-description>`.
Run: `git checkout -b <branch-name>`

## Step 3 — Commit the changes

Analyse the diff and decide how many commits make sense.
Group by **logical topic** — changes that serve the same idea or concern belong in one commit, even if they span multiple file types. Changes that serve different ideas should be separate commits, even if they're all the same file type (e.g. two unrelated markdown edits = two commits).

Examples:
- `CLAUDE.md` update + related `docs/` changes → one commit (same topic: project context)
- `.claude/commands/` changes → separate commit (different topic: Claude commands)
- Terraform module change + Lambda env var to match → one commit (same topic: the feature they jointly implement)
- Frontend component + its CSS → one commit; unrelated CI workflow fix → separate commit

For each commit:
1. Stage the relevant files: `git add <specific files>` — never `git add .` blindly
2. Write the commit message following the convention:
   - Imperative mood, sentence case, no period
   - Pattern: `<Verb> <specific subject> [to/for/from <context>]`
   - Name the exact resource/module (`API Gateway CORS`, `DynamoDB TTL`, `CloudFront TLS policy`)
   - Include reason/effect when it adds clarity
   - Avoid vague subjects
3. Run: `git commit -m "..."`

After all commits, confirm with the user before pushing if the change is large or the commit breakdown is non-obvious.

## Step 4 — Push

`git push -u origin <branch-name>`

## Step 5 — Create the PR

Draft the PR using the structure below, then run `gh pr create`.

### PR structure

**Title** — same style as commit messages: imperative mood, sentence case, no period. Describe the change precisely.

**Body:**

```
## Problem
<One or two sentences: what was wrong or missing and why it matters.>

## Change
<Bullet points naming specific files, Terraform modules, Lambda functions, React components, or workflow files changed. No vague descriptions.>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### PR rules
- Problem must state the root cause, not just symptoms
- If the branch contains only Terraform changes, note that a TFC plan run was triggered by opening this PR
- Omit Problem for pure features with no prior bug
- **Test plan:** only include if there is something concretely verifiable before merge — e.g. a unit test that can be run locally, a specific curl command, a visual check in a dev environment. Do not include a test plan for changes that can only be verified after deploying to production (most infra, CI/CD, and config changes fall into this category)
