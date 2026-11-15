# Request flood kill switch. CloudFront metrics only exist in us-east-1, so callers pass
# a us-east-1 provider. When the alarm fires, the Lambda disables the distribution to stop
# request and data transfer charges; the next Terraform apply re-enables it.

resource "aws_sns_topic" "cloudfront_alarm" {
  name = "${var.project_name}-${var.environment}-cloudfront-alarm"
  tags = var.common_tags
}

resource "aws_sns_topic_subscription" "cloudfront_alarm_email" {
  topic_arn = aws_sns_topic.cloudfront_alarm.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "cloudfront_requests" {
  alarm_name          = "${var.project_name}-${var.environment}-cloudfront-requests"
  alarm_description   = "CloudFront requests over ${var.request_alarm_threshold} in 5 minutes. Disables the distribution."
  namespace           = "AWS/CloudFront"
  metric_name         = "Requests"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = var.request_alarm_threshold
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = var.distribution_id
    Region         = "Global"
  }

  alarm_actions = [aws_sns_topic.cloudfront_alarm.arn]
  tags          = var.common_tags
}

data "archive_file" "disable_cloudfront_lambda" {
  type        = "zip"
  source_file = "../../../lambdas/disable_cloudfront.py"

  output_path = "disable_cloudfront.zip"
}

resource "aws_iam_role" "disable_cloudfront" {
  name = "${var.project_name}-${var.environment}-disable-cloudfront-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      },
    ]
  })
  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "disable_cloudfront_logs" {
  role       = aws_iam_role.disable_cloudfront.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "disable_cloudfront" {
  name = "${var.project_name}-${var.environment}-disable-cloudfront-policy"
  role = aws_iam_role.disable_cloudfront.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["cloudfront:GetDistributionConfig", "cloudfront:UpdateDistribution"]
        Effect   = "Allow"
        Resource = var.distribution_arn
      }
    ]
  })
}

resource "aws_lambda_function" "disable_cloudfront" {
  filename      = "disable_cloudfront.zip"
  function_name = "${var.project_name}-${var.environment}-lambda-disable-cloudfront"
  role          = aws_iam_role.disable_cloudfront.arn
  handler       = "disable_cloudfront.lambda_handler"
  timeout       = 30

  source_code_hash = data.archive_file.disable_cloudfront_lambda.output_base64sha256

  runtime = "python3.14"

  environment {
    variables = {
      DISTRIBUTION_ID = var.distribution_id
    }
  }
  tags = var.common_tags
}

resource "aws_lambda_permission" "disable_cloudfront_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.disable_cloudfront.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.cloudfront_alarm.arn
}

resource "aws_sns_topic_subscription" "cloudfront_alarm_lambda" {
  topic_arn = aws_sns_topic.cloudfront_alarm.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.disable_cloudfront.arn
}
