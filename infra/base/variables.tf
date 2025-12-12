variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "domain_name" {
  description = "Domain name of the app"
  type        = string
  default     = "useyourai.com"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "useyourai"
}

variable "region" {
  description = "AWS region"
  type        = string
}
