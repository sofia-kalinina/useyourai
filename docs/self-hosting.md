# Self-Hosting Guide

This guide walks through deploying your own instance of useyourai from scratch. It assumes you are comfortable with AWS, Terraform, and GitHub Actions.

---

## Prerequisites

### Accounts and tools

| What | Why |
|------|-----|
| AWS account | All infrastructure runs on AWS |
| [Terraform Cloud](https://app.terraform.io) account | Free tier is sufficient — used to run Terraform remotely |
| GitHub account | To fork the repo and run CI/CD |
| A domain in Route53 | Required for CloudFront + TLS |

### AWS Bedrock model access

The app uses `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` in `eu-central-1`. Bedrock model access is not enabled by default — you must request it manually:

1. Go to AWS Console → Bedrock → Model access (`eu-central-1`)
2. Request access to **Claude Sonnet** under Anthropic
3. Wait for approval (usually minutes, sometimes longer)

> If you want to deploy in a different region, update the model ID in all three Lambda files (`lambdas/create_session.py`, `submit_answer.py`, `retry_session.py`) and the `region` Terraform variable. The cross-region inference prefix (`eu.`) must match your region.

---

## Step 1 — Fork the repo

Fork `sofia-kalinina/useyourai` to your GitHub account.

---

## Step 2 — Set up Terraform Cloud

Create three workspaces in your TFC organization:

| Workspace | Working directory |
|-----------|-------------------|
| `<your-project>-base` | `infra/base` |
| `<your-project>-dev` | `infra/environments/dev` |
| `<your-project>-prod` | `infra/environments/prod` |

For each workspace:
- Set **Execution Mode** to `Remote`
- Connect it to your forked GitHub repo (VCS-driven workflow)
- Set the **Working Directory** to the path in the table above

---

## Step 3 — Configure workspace names

The workspace names are hardcoded in three `backend.tf` files. You have two options:

**Option A — Edit the files** (simpler)

Update `organization` and `name` in each file to match your TFC org and workspace names:
- `infra/base/backend.tf`
- `infra/environments/dev/backend.tf`
- `infra/environments/prod/backend.tf`

```hcl
terraform {
  cloud {
    organization = "<your-tfc-org>"
    workspaces {
      name = "<your-project>-base"  # or -dev / -prod
    }
  }
}
```

**Option B — Use TFC environment variables** (no source changes needed)

Set `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE` as environment variables in each TFC workspace. These override the values in `backend.tf`:

| Variable | Value |
|----------|-------|
| `TF_CLOUD_ORGANIZATION` | Your TFC organization name |
| `TF_WORKSPACE` | The workspace name (e.g. `my-project-dev`) |

---

## Step 4 — Update the GitHub Actions IAM trust policy

`infra/base/github_oidc.tf` contains an IAM role trust policy scoped to the original repo. Update the `StringLike` condition to reference your fork:

```hcl
"token.actions.githubusercontent.com:sub" = [
  "repo:<your-github-username>/<your-repo-name>:ref:refs/heads/main",
  "repo:<your-github-username>/<your-repo-name>:ref:refs/heads/main:workflow:*",
  "repo:<your-github-username>/<your-repo-name>:pull_request"
]
```

Also remove the `import` block in that file — it references a resource from the original deployment that does not exist in your account.

---

## Step 5 — Set Terraform workspace variables

Set the following Terraform variables in each workspace. Mark sensitive values as **Sensitive**.

### All three workspaces

| Variable | Example value |
|----------|---------------|
| `account_id` | Your 12-digit AWS account ID |
| `domain_name` | `yourdomain.com` |
| `project_name` | `useyourai` (or your own name) |
| `region` | `eu-central-1` |

### dev workspace only

| Variable | Example value |
|----------|---------------|
| `environment` | `dev` |
| `domain_name` | `dev.yourdomain.com` |

### prod workspace only

| Variable | Example value |
|----------|---------------|
| `environment` | `prod` |

### AWS credentials

Set these as **Environment Variables** in each TFC workspace (mark Sensitive):

| Variable | Value |
|----------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM user secret key |

The IAM user needs broad permissions to create the resources in this stack (Lambda, DynamoDB, API Gateway, Cognito, CloudFront, S3, Route53, IAM). A policy with `AdministratorAccess` is the simplest starting point — scope it down once everything is working.

---

## Step 6 — Set GitHub Actions secrets and variables

In your fork: **Settings → Secrets and variables → Actions**

| Type | Name | Value |
|------|------|-------|
| Secret | `TFC_TOKEN` | A Terraform Cloud API token (user or team token from TFC settings) |
| Variable | `TFC_WORKSPACE_DEV` | Your dev workspace ID (found in TFC workspace → General settings) |
| Variable | `TFC_WORKSPACE_PROD` | Your prod workspace ID |

The `AWS_ROLE_ARN` used by GitHub Actions is an output of the base workspace and is fetched automatically by CI/CD at deploy time — you do not need to set it manually.

---

## Step 7 — Deploy

Deploy in this order — each workspace reads outputs from the previous one.

### 1. Base workspace

Provisions the Route53 hosted zone data source, ACM certificates, and the GitHub Actions IAM role.

Trigger a plan run from the TFC UI for `<your-project>-base` and apply it.

> After this step, check your domain registrar and point your domain's nameservers to the Route53 hosted zone nameservers. DNS propagation can take up to 48 hours — ACM certificate validation will wait for it.

### 2. Dev workspace

Provisions Cognito, DynamoDB, Lambda functions, API Gateway, and CloudFront for the dev environment.

Trigger a plan run from the TFC UI for `<your-project>-dev` and apply it.

### 3. Frontend (dev)

Push any change to `ui/**` on `main` (or trigger `Deploy Frontend (dev)` manually from the Actions tab). GitHub Actions will build the React app, inject the runtime config from TFC outputs, and deploy to S3/CloudFront.

### 4. Prod workspace (optional)

Repeat steps 2–3 for prod using the `<your-project>-prod` workspace. The prod frontend deploy is manual (`workflow_dispatch` only).

---

## Verify

Once deployed:

1. Open your domain in a browser — you should see the sign-up/sign-in screen
2. Create an account and confirm via the Cognito verification email
3. Sign in and start a session — e.g. _"5 exercises on German accusative case at B1 level"_
4. Answer exercises and verify feedback is returned

---

## Estimated AWS cost

At low personal usage (dev + prod):

| Resource | Estimated monthly cost |
|----------|------------------------|
| Lambda | ~$0 (free tier) |
| DynamoDB | ~$0 (on-demand, free tier) |
| API Gateway | ~$0 (free tier) |
| CloudFront + S3 | ~$1–2 |
| Cognito | ~$0 (free tier: 50,000 MAU) |
| Bedrock (Claude Sonnet) | ~$0.003 per session |
| WAF (prod only) | ~$7/month |
| **Total** | **~$10–15/month** |
