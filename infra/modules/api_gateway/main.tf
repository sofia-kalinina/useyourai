
resource "aws_apigatewayv2_api" "useyourai_api" {
  name          = "${var.project_name}-${var.environment}-api"
  protocol_type = "HTTP"
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-api"
  })

  cors_configuration {
    allow_origins = [var.cdn_url]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type"]
  }
}


resource "aws_apigatewayv2_stage" "useyourai_api_stage" {
  api_id      = aws_apigatewayv2_api.useyourai_api.id
  name        = var.environment
  auto_deploy = true
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-api-stage"
  })
}

resource "aws_apigatewayv2_integration" "useyourai_lambdas_integration" {
  for_each           = { for lambda in var.lambdas : lambda.name => lambda }
  api_id             = aws_apigatewayv2_api.useyourai_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = each.value.invoke_arn
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "useyourai_lambdas_route" {
  for_each  = { for lambda in var.lambdas : lambda.name => lambda }
  api_id    = aws_apigatewayv2_api.useyourai_api.id
  route_key = each.value.route_key
  target    = "integrations/${aws_apigatewayv2_integration.useyourai_lambdas_integration[each.value.name].id}"
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
