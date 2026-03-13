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

```bash
gh issue edit $ARGUMENTS --add-label "in-progress"
```

## Step 3 — Create a branch from main

Always start from an up-to-date main:

```bash
git checkout main && git pull origin main && git checkout -b feature/<kebab-case-name>
```

## Step 4 — Read existing code for patterns

Before writing anything, read the existing Lambda files in `lambdas/` to understand:
- Code structure and style
- How DynamoDB and Bedrock clients are initialised at module level
- Response shape (`statusCode` + JSON `body`)

Also read `docs/implementation_plan.md`.

## Step 5 — Write the Lambda function

Create `lambdas/<function_name>.py`. Follow these patterns exactly:

**Module-level initialisation:**
```python
table_name = os.getenv('TABLE_NAME')
if not table_name:
    raise ValueError("Environment variable 'TABLE_NAME' is not set.")

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table(table_name)

bedrock = boto3.client(service_name='bedrock-runtime', region_name='eu-central-1')
INFERENCE_PROFILE_ID = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

**Critical:** all `boto3` clients and resources must specify `region_name='eu-central-1'` explicitly. Without it, CI fails at import time with `NoRegionError` because conftest fixtures run after module-level code is executed.

**Handler skeleton:**
```python
def lambda_handler(event, context):
    body_string = event.get('body')
    if not body_string:
        return {"statusCode": 400, "body": json.dumps({"error": "Request body is required"})}

    try:
        body = json.loads(body_string)
    except (json.JSONDecodeError, ValueError):
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON in request body"})}

    # validate required fields, then do work...

    return {"statusCode": 200, "body": json.dumps({...})}
```

**Bedrock invocation:**
```python
response = bedrock.invoke_model(
    modelId=INFERENCE_PROFILE_ID,
    accept="application/json",
    contentType="application/json",
    body=json.dumps({
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.7
    })
)
model_output = json.loads(response["body"].read())
text = model_output["content"][0]["text"]
```

## Step 6 — Create or update `pytest.ini`

If `pytest.ini` does not exist at the repo root, create it:

```ini
[pytest]
pythonpath = lambdas
```

This lets pytest find Lambda modules without `PYTHONPATH=lambdas`. Without it, CI fails with `ModuleNotFoundError`.

## Step 7 — Create or update `tests/conftest.py`

If `tests/conftest.py` does not exist, create it:

```python
import os
import pytest

@pytest.fixture(autouse=True, scope="session")
def aws_credentials():
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
    os.environ.setdefault("AWS_SECURITY_TOKEN", "testing")
    os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
    os.environ.setdefault("AWS_DEFAULT_REGION", "eu-central-1")
```

Note: this fixture does **not** set `TABLE_NAME` or region early enough for module-level code. Region must be explicit in the Lambda (Step 5). `TABLE_NAME` must be set in the test file itself (Step 8).

## Step 8 — Write pytest tests

Create `tests/test_<function_name>.py`. Check existing test files for style.

**Critical ordering** — set `TABLE_NAME` before importing the Lambda module:

```python
import os
os.environ["TABLE_NAME"] = "test-table"

import <function_name>  # noqa: E402
```

**DynamoDB fixture** — use `mock_aws`, create the table, then replace the module-level table reference:

```python
from moto import mock_aws

@pytest.fixture
def dynamodb_table():
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="eu-central-1")
        table = ddb.create_table(
            TableName="test-table",
            KeySchema=[
                {"AttributeName": "session_id", "KeyType": "HASH"},
                {"AttributeName": "question_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "session_id", "AttributeType": "S"},
                {"AttributeName": "question_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        <function_name>.table = table  # replace module-level reference
        yield table
```

**Bedrock mocking** — do NOT use moto for Bedrock. Use `unittest.mock.patch.object` on the module's bedrock client:

```python
from unittest.mock import MagicMock, patch

def bedrock_response_for(data):
    body_bytes = json.dumps({"content": [{"type": "text", "text": json.dumps(data)}]}).encode()
    mock_body = MagicMock()
    mock_body.read.return_value = body_bytes
    return {"body": mock_body}

def test_something(dynamodb_table):
    with patch.object(<function_name>.bedrock, "invoke_model", return_value=bedrock_response_for(FAKE_DATA)):
        response = <function_name>.lambda_handler(event, {})
    assert response["statusCode"] == 200
```

**DynamoDB read-back** — boto3 resource returns `Decimal` for numbers; cast when asserting:
```python
assert int(item["feedback_every_n"]) == 3
```

Test coverage to aim for:
- Happy path: 200 + correct DynamoDB items written + correct response shape
- Each required field missing → 400
- Invalid JSON body → 400
- Claude returns invalid JSON → 502

## Step 9 — Run tests locally

```bash
pytest tests/test_<function_name>.py -v
```

Fix all failures before continuing.

Also validate the SAM template if it exists:
```bash
sam validate --template template.yaml
```

## Step 10 — Create or update `requirements-dev.txt`

Ensure it contains:
```
boto3>=1.34.0
moto[dynamodb]>=5.0.0
pytest>=8.0.0
```

Only add `moto[bedrock]` if you are actually using moto to mock Bedrock (we use `unittest.mock` instead, so it is not needed).

## Step 11 — Create or update `.github/workflows/test-lambdas.yml`

If it does not exist, create it:

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
        run: pip install -r requirements-dev.txt
      - name: Run Lambda tests
        run: pytest tests/ -v
```

## Step 12 — Add Terraform infra changes

On the same branch, commit the Terraform changes needed to deploy the Lambda.

**`infra/modules/lambdas/main.tf`** — add archive + function:
```hcl
data "archive_file" "<name>_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/<file>.py"
  output_path = "<file>.zip"
}

resource "aws_lambda_function" "<name>_lambda" {
  filename         = "<file>.zip"
  function_name    = "${var.project_name}-${var.environment}-lambda-<name>"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "<file>.lambda_handler"
  timeout          = 30
  source_code_hash = data.archive_file.<name>_lambda.output_base64sha256
  runtime          = "python3.11"

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
  tags = merge(var.common_tags, { Name = "${var.project_name}-${var.environment}-lambda-<name>" })
}
```

**`infra/modules/lambdas/outputs.tf`** — add outputs:
```hcl
output "<name>_lambda_name" {
  value = aws_lambda_function.<name>_lambda.function_name
}
output "<name>_lambda_invoke_arn" {
  value = aws_lambda_function.<name>_lambda.invoke_arn
}
```

**`infra/environments/dev/main.tf` and `prod/main.tf`** — add route to the `api_gateway` lambdas list:
```hcl
{
  name       = module.lambdas.<name>_lambda_name
  invoke_arn = module.lambdas.<name>_lambda_invoke_arn
  route_key  = "POST /<route>"
}
```

No IAM changes needed — the shared Lambda execution role already has DynamoDB and Bedrock policies.

Commit the Terraform changes as a separate commit on the same branch:
```bash
git add infra/
git commit -m "Add <name> Lambda and POST /<route> route to API Gateway"
```

## Step 13 — Open a PR

```bash
gh pr create \
  --title "Add <FunctionName> Lambda for <purpose>" \
  --body "$(cat <<'EOF'
## Change
- `lambdas/<file>.py` — <what it does>
- `tests/test_<file>.py` — <N> pytest tests covering <what>
- `pytest.ini`, `tests/conftest.py`, `requirements-dev.txt`, `.github/workflows/test-lambdas.yml` — test infrastructure (if new)
- `infra/modules/lambdas/main.tf` — new Lambda resource
- `infra/modules/lambdas/outputs.tf` — name and invoke_arn outputs
- `infra/environments/dev/main.tf`, `infra/environments/prod/main.tf` — POST /<route> route added

Opening this PR triggers a Terraform Cloud plan run for dev and prod workspaces.

## Test plan
- [x] pytest passes locally
- [x] SAM template validates
- [ ] GitHub Actions test workflow runs on this PR

Closes #$ARGUMENTS

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Step 14 — Update the GitHub issue

```bash
gh issue comment $ARGUMENTS --body "<pr-url>"
gh issue edit $ARGUMENTS --add-label "in-progress"
```

Return the PR URL to the user.
