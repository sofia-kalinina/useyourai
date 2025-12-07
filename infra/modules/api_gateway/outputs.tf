output "api_gateway_invoke_url" {
  description = "The invoke URL of the API Gateway"
  value       = aws_apigatewayv2_api.useyourai_api.api_gateway_invoke_url
}
