# Contributing to useyourai

Thanks for your interest. This document covers how to set up the project locally, the branch and PR conventions, and what to expect when contributing.

---

## Project overview

Before diving in, read [README.md](README.md) for the architecture overview and [docs/implementation_plan.md](docs/implementation_plan.md) for the full Lambda and API design, including what the architecture deliberately avoids and why. The key principle: each Lambda is fully self-contained — no Lambda-to-Lambda calls, evaluation is inline with the request that needs it.

---

## Local setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- A deployed instance of the backend (or use the dev environment at `dev.useyourai.eu`)

### Frontend

```bash
cp ui/public/config.js.example ui/public/config.js
# Fill in config.js with your API Gateway URL and Cognito pool details
cd ui && npm install && npm start
```

The dev server runs at [http://localhost:3000](http://localhost:3000).

### Lambda tests

```bash
pip install -r requirements-dev.txt
pytest
```

No AWS credentials needed — DynamoDB is mocked with [moto](https://github.com/getmoto/moto) and Bedrock calls are mocked with `unittest.mock`.

---

## Making changes

### Branches

Always work on a branch — never commit directly to `main`.

| Type | Pattern | Example |
|------|---------|---------|
| New feature | `feature/<kebab-case>` | `feature/suggest-topic-lambda` |
| Bug fix | `fix/<kebab-case>` | `fix/missing-user-id-guard` |
| Docs / chore | `docs/<kebab-case>` or `chore/<kebab-case>` | `docs/api-reference` |

### Commit messages

Imperative mood, sentence case, no period. Name the specific thing that changed and include the reason when it adds clarity:

```
Add suggestTopic Lambda (POST /suggest)
Fix API Gateway CORS origin for dev.useyourai.eu
Update config.js.example to include Cognito fields
```

### Pull requests

- Keep PRs focused — one logical change per PR
- If your change touches `infra/`, opening a PR automatically triggers a Terraform Cloud plan run for the dev workspace. Review the plan output before merging.
- If your change touches `ui/`, run `npm run build` locally to confirm there are no compilation errors before opening the PR.

---

## Backend (Lambda) guidelines

- **Prompt injection hardening is required** for any Lambda that passes user input to Claude. Wrap user-controlled strings in XML tags (`<user_prompt>`, `<user_answer>`) and add an explicit instruction in the system prompt to treat tagged content as data only. Cap input lengths before the Bedrock call.
- **Validate Claude's response schema** — don't assume the structure is correct. Return 502 if Claude returns malformed JSON or a schema that doesn't match expectations.
- **All `boto3` clients must specify `region_name='eu-central-1'` explicitly** — without it, tests fail at import time with `NoRegionError`.
- **Write tests for new Lambdas** — see `tests/` for patterns. Cover the happy path, each required-field missing case, invalid JSON body, and Claude returning malformed responses.

---

## Infrastructure guidelines

- Infrastructure is deployed via **Terraform Cloud** — do not run `terraform apply` locally.
- No copy-paste Terraform — use modules. The existing modules in `infra/modules/` cover the common patterns.
- IAM: least-privilege. No wildcard resources unless genuinely necessary.
- All tool versions must be pinned.

---

## What's out of scope

- Lambda-to-Lambda calls — keep each Lambda self-contained
- Clever Python — readable and boring is the goal
- Hardcoded secrets, API keys, or account IDs anywhere in code or config

---

## Questions

Open a [GitHub issue](https://github.com/sofia-kalinina/useyourai/issues) if something is unclear or you want to discuss a change before building it.
