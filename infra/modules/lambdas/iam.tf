data "aws_kms_alias" "lambda" {
  name = "alias/aws/lambda"
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "LambdaExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "dynamodb_rw_access_policy" {
  name = "DynamodbRWAccess"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:DeleteItem"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:dynamodb:${var.region}:${var.account_id}:table/LanguageLearningTable-${var.environment}"
      }
    ]
  })
}


# Using the aws managed key to save costs
resource "aws_iam_role_policy" "lambda_kms_key_access_policy" {
  name = "LambdaKMSKeyAccess"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Effect   = "Allow"
        Resource = data.aws_kms_alias.lambda.target_key_arn
      }
    ]
  })
}

# TODO: narrow the permissions down to the models needed for the app logic
resource "aws_iam_role_policy" "bedrock_invoke_models_policy" {
  name = "BedrockInvokeModelsAccess"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}
