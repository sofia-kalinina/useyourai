variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "managed_by_github_actions" {
  description = "If true, GitHub actions will have permissions to change the resources"
  type        = bool
  default     = false
}
