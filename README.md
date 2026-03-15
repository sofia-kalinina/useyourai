# useyourai

[![Deploy Frontend](https://img.shields.io/github/actions/workflow/status/sofia-kalinina/useyourai/deploy-frontend.yml?branch=main&label=deploy&style=flat-square)](https://github.com/sofia-kalinina/useyourai/actions/workflows/deploy-frontend.yml)
[![Test Lambdas](https://img.shields.io/github/actions/workflow/status/sofia-kalinina/useyourai/test-lambdas.yml?branch=main&label=tests&style=flat-square)](https://github.com/sofia-kalinina/useyourai/actions/workflows/test-lambdas.yml)

> AI-powered language grammar practice, on demand — no account required.

`useyourai` is a serverless language learning app that generates personalized grammar exercises through a chat interface. Describe what you want to practice, get exercises one by one, and receive AI-generated feedback at configurable intervals. Built end-to-end on AWS with Claude Sonnet via Bedrock.

Live: [useyourai.eu](https://useyourai.eu) · Dev: [dev.useyourai.eu](https://dev.useyourai.eu)

## Features

- **On-demand exercise generation** — describe a topic in plain text (e.g. *"10 sentences to practice German accusative case"*) and Claude generates a structured exercise set
- **One-by-one practice** — exercises are presented individually; each answer is evaluated by Claude
- **Configurable feedback** — set how often you receive textual feedback (e.g. every 3 answers)
- **Retry mistakes** — after completing a session, get a new targeted exercise set focused on what you got wrong
- **No account needed** — sessions are stored temporarily (24h TTL) and then auto-deleted

## Architecture

```
Browser (React)
  └─▶ CloudFront ──▶ S3 (static assets)
  └─▶ API Gateway (HTTP)
        ├─▶ POST /session          → create_session Lambda
        └─▶ POST /session/{id}/answer → submit_answer Lambda
                ├─▶ AWS Bedrock (Claude Sonnet 4.5)
                └─▶ DynamoDB
```

| Layer | Technology |
|---|---|
| Frontend | React 18, Axios |
| Backend | AWS Lambda (Python 3.11) |
| AI | AWS Bedrock — Claude Sonnet 4.5 (`eu-central-1`) |
| Database | DynamoDB (on-demand, TTL-based cleanup) |
| API | AWS API Gateway (HTTP) |
| CDN | CloudFront + S3 |
| IaC | Terraform + Terraform Cloud |
| CI/CD | GitHub Actions (OIDC, no long-lived credentials) |

## Project Structure

```
.
├── lambdas/           # Python Lambda functions
│   ├── create_session.py    # POST /session — generate exercises
│   └── submit_answer.py     # POST /session/{id}/answer — evaluate answers
├── ui/                # React frontend
│   └── src/
│       ├── App.js
│       ├── Chat.js          # Main chat interface and session logic
│       └── Message.js
├── infra/             # Terraform modules and environments
│   ├── modules/       # api_gateway, lambdas, dynamodb, frontend
│   └── environments/  # dev, prod
├── tests/             # Python unit tests (moto for DynamoDB mocking)
└── .github/workflows/ # CI/CD: frontend deploy + Lambda tests
```

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- AWS credentials (for local Lambda testing only)

### Frontend

Run `/setup-frontend` to install dependencies and configure the API URL, then `/start-frontend-locally` to start the dev server on http://localhost:3000.

The frontend reads the API URL from `window.ENV.API_URL` (injected via `ui/public/config.js`). For local development you need to copy the example config and set it to your API Gateway dev URL — `/setup-frontend` handles this.

### Lambda tests

Run `/test-lambdas` to install dependencies and run the full pytest suite.

## Deployment

Infrastructure is managed by **Terraform Cloud** — do not run `terraform apply` locally.

- **Workspaces:** https://app.terraform.io/app/sofiia-kalinina/workspaces/
- **Frontend deploy:** automatic on push to `main` (GitHub Actions syncs the React build to S3 and invalidates CloudFront)
- **Lambda deploy:** handled by Terraform when Lambda source files change

> [!NOTE]
> The CI/CD pipeline fetches Terraform outputs (API Gateway URL, S3 bucket, CloudFront distribution ID) to generate `config.js` and deploy the frontend without any hardcoded values.

## How It Works

1. **Start a session** — type a prompt like *"Give me 5 exercises on French past tense"*. The app calls `POST /session`, which asks Claude to generate structured exercises, stores them in DynamoDB, and returns the first one.

2. **Answer exercises** — each answer is submitted to `POST /session/{id}/answer`. Claude evaluates correctness, and textual feedback is generated every N answers (configurable per session).

3. **Retry mistakes** — when the session ends, the app shows how many answers were wrong and offers to start a focused retry session. *(Coming in Sprint 3)*

## Roadmap

- [ ] `POST /session/{id}/retry` — targeted retry sessions based on mistakes
- [ ] Secure API Gateway (rate limiting, auth)
- [ ] Production environment
- [ ] CloudWatch structured logging
- [ ] User accounts and study history
