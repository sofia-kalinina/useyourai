# Implement Lambda from GitHub Issue

Implement a Lambda function task end-to-end from a GitHub issue.

**Issue number:** $ARGUMENTS

---

## Step 1 — Fetch the GitHub issue

```bash
gh issue view $ARGUMENTS
```

Extract: title, body. This is your full spec.

## Step 2 — Move issue to In Progress

Add the `in-progress` label:
```bash
gh issue edit $ARGUMENTS --add-label "in-progress"
```

## Step 3 — Create a branch

Branch name: `feature/<kebab-case-card-name>` or `fix/<kebab-case-card-name>` depending on context.

```bash
git checkout -b <branch-name>
```

## Step 4 — Read existing code for patterns

Before writing anything, read the existing Lambda files in `lambdas/` to understand:
- Code structure and style
- How DynamoDB is initialised (module-level, using `TABLE_NAME` env var sourced from Terraform)
- How Bedrock is called
- Response shape (`statusCode` + JSON `body`)

Also read `docs/implementation_plan.md` if it exists.

## Step 5 — Write or edit the Lambda function

Create or update the relevant file in `lambdas/`. Follow the patterns from existing Lambdas:
- Python 3.11
- `lambda_handler(event, context)` entry point
- Read table name from `os.getenv('TABLE_NAME')` — injected by Terraform at deploy time
- Return `{"statusCode": <int>, "body": json.dumps({...})}`
- Parse request body with `json.loads(event.get('body'))`
- Validate inputs and return 400 for bad requests

## Step 6 — Create or update `template.yaml`

If `template.yaml` does not exist, create it at the repo root. If it exists, add or update the relevant function.

The template must include ALL Lambda functions currently in `lambdas/` (not just the new one). Check what `.py` files exist in `lambdas/` and include each one.

Use this structure as a base, extending it for all functions:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: useyourai Lambda functions

Globals:
  Function:
    Runtime: python3.11
    Timeout: 30
    Environment:
      Variables:
        TABLE_NAME: !Sub "${AWS::StackName}-table-language-learning"

Resources:
  InitSessionFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: init_session
      CodeUri: lambdas/
      Handler: init_session.lambda_handler
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Sub "${AWS::StackName}-table-language-learning"
      Events:
        Api:
          Type: Api
          Properties:
            Path: /init
            Method: post

  TestBedrockFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: test_bedrock
      CodeUri: lambdas/
      Handler: test_bedrock.lambda_handler
      Policies:
        - Statement:
            - Effect: Allow
              Action:
                - bedrock:InvokeModel
              Resource: "*"
      Events:
        Api:
          Type: Api
          Properties:
            Path: /test
            Method: post

  # Add new function here following the same pattern
```

## Step 7 — Write pytest tests

Create a test file `tests/test_<function_name>.py`. Use `moto` to mock AWS services.

Test structure guidelines:
- For functions that write to DynamoDB: mock the table, invoke the handler, assert the item was written and the response has `statusCode: 200`
- For functions that call Bedrock: mock `bedrock-runtime` with `moto`, or patch `boto3.client` to return a fake response; assert the reply is returned in the response body
- For validation logic: test missing/malformed body returns `statusCode: 400`
- Use `@pytest.fixture` for repeated setup (e.g. mocked DynamoDB table)
- Set `TABLE_NAME=test-table` in the test environment

Check `tests/` for existing test files and follow their style.

## Step 8 — Run tests locally

```bash
pytest tests/test_<function_name>.py -v
```

Fix any failures before continuing.

Also confirm SAM can parse the template (no Docker needed for validation):
```bash
sam validate --template template.yaml
```

If SAM CLI is not installed, note this in the PR description so the user can install it.

## Step 9 — Create or update `.github/workflows/test-lambdas.yml`

If the file does not exist, create it. If it exists, add the new function's test to it.

```yaml
name: Test Lambdas

on:
  pull_request:
    paths:
      - 'lambdas/**'
      - 'tests/**'
      - 'template.yaml'
      - 'requirements*.txt'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt

      - name: Run Lambda tests
        run: |
          pytest tests/ -v
```

Check that `requirements-dev.txt` includes `pytest`, `moto[dynamodb]`, `moto[bedrock]`, and `boto3`. Add any missing packages.

## Step 10 — Commit and push

Stage only relevant files (Lambda source, tests, template.yaml, workflow, requirements):
```bash
git add lambdas/<file>.py tests/test_<file>.py template.yaml .github/workflows/test-lambdas.yml requirements-dev.txt
git commit -m "<Verb> <specific subject> [reason if helpful]"
git push -u origin <branch-name>
```

Commit message rules (from CLAUDE.md):
- Imperative mood, sentence case, no period
- Name the exact resource: e.g. `Add createSession Lambda for exercise generation`

If any context files (CLAUDE.md, docs/, .claude/commands/) need updating as a result of this work, add them as a separate commit on the same branch.

## Step 11 — Open a PR

Use the `## Change` format (no `## Problem` for pure features). Include `Closes #$ARGUMENTS` in the body so GitHub auto-closes the issue on merge:

```bash
gh pr create \
  --title "<title matching commit message style>" \
  --body "$(cat <<'EOF'
## Change
- <bullet points naming specific files changed>

## Test plan
- [ ] pytest passes locally
- [ ] SAM template validates (`sam validate`)
- [ ] GitHub Actions test workflow runs on this PR

Closes #$ARGUMENTS

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Step 12 — Update the GitHub issue

Comment the PR URL on the issue and confirm the `in-progress` label is set:
```bash
gh issue comment $ARGUMENTS --body "<pr-url>"
gh issue edit $ARGUMENTS --add-label "in-progress"
```

Return the PR URL to the user.
