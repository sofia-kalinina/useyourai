variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "domain_name" {
  description = "Domain name of the app"
  type        = string
  default     = "useyourai.eu"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "useyourai"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "tags" {
  description = "Map of tags to assign to resources"
  type        = map(string)
  default     = {}
}
