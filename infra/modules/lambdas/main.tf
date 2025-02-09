data "archive_file" "init_session_lambda" {
  type        = "zip"
  source_file = "init_session.py"
  output_path = "init_session.zip"
}

resource "aws_lambda_function" "init_session_lambda" {
  filename      = "init_session.zip"
  function_name = "init_session"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "init_session.lambda_handler"

  source_code_hash = data.archive_file.init_session_lambda.output_base64sha256

  runtime = "python3.11"

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}