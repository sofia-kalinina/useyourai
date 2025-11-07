variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "useyourai"
}

variable "tags" {
  description = "Map of tags to assign to resources"
  type        = map(string)
  default     = {}
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
