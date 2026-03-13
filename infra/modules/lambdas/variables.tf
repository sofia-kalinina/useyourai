variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
}

variable "account_id" {
  description = "AWS account ID"
  type        = string  
}

variable "environment" {
  description = "Environment name"
  type        = string  
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  type        = string
}
