data "archive_file" "init_session_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/init_session.py"

  output_path = "init_session.zip"
}

resource "aws_lambda_function" "init_session_lambda" {
  filename      = "init_session.zip"
  function_name = "${var.project_name}-${var.environment}-lambda-init-session"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "init_session.lambda_handler"

  source_code_hash = data.archive_file.init_session_lambda.output_base64sha256

  runtime = "python3.11"

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-lambda-init-session"
  })
}

data "archive_file" "create_session_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/create_session.py"

  output_path = "create_session.zip"
}

resource "aws_lambda_function" "create_session_lambda" {
  filename      = "create_session.zip"
  function_name = "${var.project_name}-${var.environment}-lambda-create-session"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "create_session.lambda_handler"
  timeout       = 30

  source_code_hash = data.archive_file.create_session_lambda.output_base64sha256

  runtime = "python3.11"

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-lambda-create-session"
  })
}

data "archive_file" "submit_answer_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/submit_answer.py"
  output_path = "submit_answer.zip"
}

resource "aws_lambda_function" "submit_answer_lambda" {
  filename         = "submit_answer.zip"
  function_name    = "${var.project_name}-${var.environment}-lambda-submit-answer"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "submit_answer.lambda_handler"
  timeout          = 30
  source_code_hash = data.archive_file.submit_answer_lambda.output_base64sha256
  runtime          = "python3.11"

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
  tags = merge(var.common_tags, { Name = "${var.project_name}-${var.environment}-lambda-submit-answer" })
}

data "archive_file" "retry_session_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/retry_session.py"
  output_path = "retry_session.zip"
}

resource "aws_lambda_function" "retry_session_lambda" {
  filename         = "retry_session.zip"
  function_name    = "${var.project_name}-${var.environment}-lambda-retry-session"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "retry_session.lambda_handler"
  timeout          = 30
  source_code_hash = data.archive_file.retry_session_lambda.output_base64sha256
  runtime          = "python3.11"

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
  tags = merge(var.common_tags, { Name = "${var.project_name}-${var.environment}-lambda-retry-session" })
}

data "archive_file" "test_bedrock_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/test_bedrock.py"

  output_path = "test_bedrock.zip"
}

resource "aws_lambda_function" "test_bedrock_lambda" {
  filename      = "test_bedrock.zip"
  function_name = "${var.project_name}-${var.environment}-lambda-test-bedrock"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "test_bedrock.lambda_handler"
  timeout       = 30

  source_code_hash = data.archive_file.test_bedrock_lambda.output_base64sha256

  runtime = "python3.11"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-lambda-test-bedrock"
  })
}
