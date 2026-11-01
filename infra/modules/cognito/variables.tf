variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
}

variable "allow_admin_create_user_only" {
  description = "When true, only an admin can create users and self-service sign-up is disabled"
  type        = bool
  default     = false
}
