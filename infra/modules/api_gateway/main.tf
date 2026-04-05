
resource "aws_apigatewayv2_api" "useyourai_api" {
  name          = "${var.project_name}-${var.environment}-api"
  protocol_type = "HTTP"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-api"
  })

  cors_configuration {
    allow_origins = compact(["https://${var.cdn_url}", var.custom_domain_name != "" ? "https://${var.custom_domain_name}" : ""])
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
  }
}


resource "aws_apigatewayv2_stage" "useyourai_api_stage" {
  api_id      = aws_apigatewayv2_api.useyourai_api.id
  name        = var.environment
  auto_deploy = true
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-api-stage"
  })

  default_route_settings {
    throttling_rate_limit  = var.throttling_rate_limit
    throttling_burst_limit = var.throttling_burst_limit
  }
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.useyourai_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "${var.project_name}-${var.environment}-cognito-authorizer"

  jwt_configuration {
    issuer   = var.cognito_user_pool_endpoint
    audience = [var.cognito_user_pool_client_id]
  }
}

resource "aws_apigatewayv2_integration" "useyourai_lambdas_integration" {
  for_each               = { for lambda in var.lambdas : lambda.name => lambda }
  api_id                 = aws_apigatewayv2_api.useyourai_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = each.value.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "useyourai_lambdas_route" {
  for_each             = { for lambda in var.lambdas : lambda.name => lambda }
  api_id               = aws_apigatewayv2_api.useyourai_api.id
  route_key            = each.value.route_key
  target               = "integrations/${aws_apigatewayv2_integration.useyourai_lambdas_integration[each.value.name].id}"
  authorization_type   = "JWT"
  authorizer_id        = aws_apigatewayv2_authorizer.cognito.id
}

# Permission for API Gateway to invoke Lambdas
resource "aws_lambda_permission" "apigw" {
  for_each      = { for lambda in var.lambdas : lambda.name => lambda }
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = each.key
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.useyourai_api.execution_arn}/*/*"
}
