# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A serverless AI-powered language learning app focused on grammar. Users request exercises via a chat interface; Claude Sonnet 4.5 (AWS Bedrock) generates exercises and feedback.

- **Current iteration (v1):** authenticated users (Cognito), full exercise flow with retry — see `docs/implementation_plan.md` (loaded automatically for `lambdas/` work)
- **Long-term vision:** user accounts, study history, per-topic statistics and success rates
- **Project planning:** GitHub Issues — repo: https://github.com/sofia-kalinina/useyourai

**Background:** I'm a DevOps Engineer building this end-to-end, including frontend — deliberate practice to strengthen full-stack and AWS skills, not just a side project. I chose this stack to learn it deeply.

## Tech Stack

- **IaC:** Terraform + Terraform Cloud (org: `sofiia-kalinina`)
- **CI/CD:** GitHub Actions
- **Backend:** AWS Lambda (Python 3.14)
- **Database:** AWS DynamoDB
- **API:** AWS API Gateway (HTTP)
- **Frontend:** React 18
- **AI:** AWS Bedrock — `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`

Region: `eu-central-1`.

All tool versions must be pinned and up-to-date. Prefer tools with strong community adoption.

## Commands

### Frontend (ui/)
```bash
cd ui && npm start        # Dev server on localhost:3000
cd ui && npm run build    # Production build
cd ui && npm test         # Run tests
```

### Lambda testing
```bash
pytest                    # Run Python tests from root
```

## Repo Map

- `lambdas/` — Python handlers, see `lambdas/CLAUDE.md`
- `ui/` — React app, API and Cognito config injected via `ui/public/config.js`
- `infra/` — Terraform: `base`, `environments/dev` and `prod`, `modules/`

## Rules — Always Follow

@.claude/rules.md

- **Be opinionated:** If I ask for something that doesn't make sense, say so clearly before doing it. I want pushback, not blind execution.
- **Atomic changes:** Every change should be scoped, explainable, and independently reviewable. No surprise refactors bundled with features.
- **Warn on contradiction:** If a request conflicts with anything in this file, flag it explicitly and ask me to confirm before proceeding.
- **Security defaults:** IAM least-privilege, no wildcard permissions, secrets in Parameter Store or Secrets Manager — never hardcoded.
- **Cost awareness:** Flag architectural choices that could unexpectedly increase AWS spend (Lambda cold starts, DynamoDB read/write costs, over-provisioning).
- **Backend simplicity:** Python code should be readable and boring, not clever.
- **Prompt injection hardening:** All user-controlled strings passed to Claude must be wrapped in XML tags (e.g. `<user_prompt>`, `<user_answer>`) and length-capped before reaching Bedrock. Each system prompt must include an explicit instruction to treat tagged content as data only.
- **DRY infrastructure:** No copy-paste Terraform.
- **Explain the why:** When introducing patterns, explain the reasoning — I'm here to learn, not just ship.

## Git Workflow

- Always work on a branch — never commit directly to `main`
- Branch naming: `feature/<kebab-case-description>` for new work, `fix/<kebab-case-description>` for bug fixes
- After pushing, always open a PR — this triggers a Terraform Cloud plan run automatically
- After opening a PR, comment the PR link on the related GitHub issue
- Commit messages: imperative mood, sentence case, no period — `<Verb> <specific subject> [to/for/from <context>]`
  - Name the exact resource/module (`API Gateway CORS`, `Route53 CNAME record`, `CloudFront TLS policy`)
  - Include the reason/effect when it adds clarity (`to allow CORS requests from dev.useyourai.eu`)
  - Avoid vague subjects; be precise about what changed

## Infrastructure Deployment (Terraform)

Deployed via **Terraform Cloud**, not locally.

- Workspaces: https://app.terraform.io/app/sofiia-kalinina/workspaces/
- Auth: `terraform login` (credentials in `~/.terraform.d/credentials.tfrc.json`)

Do **not** run `terraform apply` locally. Use the TFC API or queue a run in the Terraform Cloud UI.

Prod release: merge to `main`, test on dev, push a version tag such as `1.0.0` (no `v`), apply the prod run in Terraform Cloud, then run `Deploy Frontend (prod)` on the tag.
