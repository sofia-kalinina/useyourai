output "init_session_lambda_name" {
  value = aws_lambda_function.init_session_lambda.function_name

}
output "test_bedrock_lambda_name" {
  value = aws_lambda_function.test_bedrock_lambda.function_name
}

output "init_session_lambda_invoke_arn" {
  value = aws_lambda_function.init_session_lambda.invoke_arn

}
output "test_bedrock_lambda_invoke_arn" {
  value = aws_lambda_function.test_bedrock_lambda.invoke_arn
}
