resource "aws_apigatewayv2_api" "useyourai_api" {
  name          = "LanguageLearningAPI-${var.environment}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.useyourai_api.id
  name        = "$default"
  auto_deploy = true
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
