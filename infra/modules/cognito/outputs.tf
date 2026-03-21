output "user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.main.id
}

output "user_pool_endpoint" {
  description = "Cognito User Pool issuer URL for the JWT authorizer"
  value       = "https://${aws_cognito_user_pool.main.endpoint}"
}
