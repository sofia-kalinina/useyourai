Create a pull request for the current branch following the project conventions.

Steps:
1. Run `git log main..HEAD --oneline` to see all commits on this branch
2. Run `git diff main...HEAD --stat` to see files changed
3. Draft a PR using the structure below, then run `gh pr create` with it

## PR structure

**Title** — same style as commit messages: imperative mood, sentence case, no period. Describe the change precisely (name the resource/module affected).

**Body:**

```
## Problem
<One or two sentences explaining what was wrong or missing and why it matters.>

## Change
<Bullet points describing what was changed, naming specific files/modules/resources.>

## Test plan
- [ ] <Specific thing to verify — name the environment, resource, or behaviour to check>
- [ ] <Another verification step>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Rules
- Problem section must state the *root cause*, not just symptoms
- Change section must reference specific Terraform modules, Lambda functions, React components, or workflow files — no vague descriptions
- Test plan steps must be concrete and checkable, not generic ("verify it works")
- If the branch contains only Terraform changes, note that a TFC plan run was triggered by this PR
- Do not include sections that don't apply (e.g. no Test plan for doc-only changes)
