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

data "archive_file" "suggest_topic_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/suggest_topic.py"
  output_path = "suggest_topic.zip"
}

resource "aws_lambda_function" "suggest_topic_lambda" {
  filename         = "suggest_topic.zip"
  function_name    = "${var.project_name}-${var.environment}-lambda-suggest-topic"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "suggest_topic.lambda_handler"
  timeout          = 30
  source_code_hash = data.archive_file.suggest_topic_lambda.output_base64sha256
  runtime          = "python3.11"
  tags             = merge(var.common_tags, { Name = "${var.project_name}-${var.environment}-lambda-suggest-topic" })
}

