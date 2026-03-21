output "create_session_lambda_name" {
  value = aws_lambda_function.create_session_lambda.function_name
}

output "create_session_lambda_invoke_arn" {
  value = aws_lambda_function.create_session_lambda.invoke_arn
}

output "submit_answer_lambda_name" {
  value = aws_lambda_function.submit_answer_lambda.function_name
}

output "submit_answer_lambda_invoke_arn" {
  value = aws_lambda_function.submit_answer_lambda.invoke_arn
}

output "retry_session_lambda_name" {
  value = aws_lambda_function.retry_session_lambda.function_name
}

output "retry_session_lambda_invoke_arn" {
  value = aws_lambda_function.retry_session_lambda.invoke_arn
}

