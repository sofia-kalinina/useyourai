variable "common_tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "distribution_id" {
  description = "ID of the CloudFront distribution to watch and disable"
  type        = string
}

variable "distribution_arn" {
  description = "ARN of the CloudFront distribution to watch and disable"
  type        = string
}

variable "alert_email" {
  description = "Email address that receives the alarm"
  type        = string
}

variable "request_alarm_threshold" {
  description = "CloudFront requests in 5 minutes above which the distribution is disabled"
  type        = number
  default     = 50000
}
