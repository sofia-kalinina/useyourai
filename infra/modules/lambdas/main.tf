data "archive_file" "create_session_lambda" {
  type = "zip"
  source {
    content  = file("../../../lambdas/create_session.py")
    filename = "create_session.py"
  }
  source {
    content  = file("../../../lambdas/cefr_level_guide.md")
    filename = "cefr_level_guide.md"
  }
  source {
    content  = file("../../../lambdas/exercise_formats.md")
    filename = "exercise_formats.md"
  }
  source {
    content  = file("../../../lambdas/generation_docs.py")
    filename = "generation_docs.py"
  }

  output_path = "create_session.zip"
}

resource "aws_lambda_function" "create_session_lambda" {
  filename      = "create_session.zip"
  function_name = "${var.project_name}-${var.environment}-lambda-create-session"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "create_session.lambda_handler"
  timeout       = 30

  source_code_hash = data.archive_file.create_session_lambda.output_base64sha256

  runtime = "python3.14"

  environment {
    variables = {
      TABLE_NAME         = var.dynamodb_table_name
      GLOBAL_DAILY_LIMIT = var.global_daily_limit
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
  runtime          = "python3.14"

  environment {
    variables = {
      TABLE_NAME         = var.dynamodb_table_name
      GLOBAL_DAILY_LIMIT = var.global_daily_limit
    }
  }
  tags = merge(var.common_tags, { Name = "${var.project_name}-${var.environment}-lambda-submit-answer" })
}

data "archive_file" "retry_session_lambda" {
  type = "zip"
  source {
    content  = file("../../../lambdas/retry_session.py")
    filename = "retry_session.py"
  }
  source {
    content  = file("../../../lambdas/cefr_level_guide.md")
    filename = "cefr_level_guide.md"
  }
  source {
    content  = file("../../../lambdas/exercise_formats.md")
    filename = "exercise_formats.md"
  }
  source {
    content  = file("../../../lambdas/generation_docs.py")
    filename = "generation_docs.py"
  }
  output_path = "retry_session.zip"
}

resource "aws_lambda_function" "retry_session_lambda" {
  filename         = "retry_session.zip"
  function_name    = "${var.project_name}-${var.environment}-lambda-retry-session"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "retry_session.lambda_handler"
  timeout          = 30
  source_code_hash = data.archive_file.retry_session_lambda.output_base64sha256
  runtime          = "python3.14"

  environment {
    variables = {
      TABLE_NAME         = var.dynamodb_table_name
      GLOBAL_DAILY_LIMIT = var.global_daily_limit
    }
  }
  tags = merge(var.common_tags, { Name = "${var.project_name}-${var.environment}-lambda-retry-session" })
}

