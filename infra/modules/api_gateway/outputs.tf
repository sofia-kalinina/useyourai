output "api_gateway_url" {
  description = "The base URL of the API Gateway"
  value       = aws_apigatewayv2_api.useyourai_api.api_endpoint
}
