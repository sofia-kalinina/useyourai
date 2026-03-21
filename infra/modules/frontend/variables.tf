variable "common_tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
}

variable "certificate_arn" {
  description = "ARN of ACM certificate"
  type        = string
  default     = null
}

variable "domain_name" {
  description = "Domain name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "hosted_zone_id" {
  description = "ID of Route53 hosted zone to create record"
}

variable "github_actions_role_name" {
  description = "Name of the shared IAM role used by GitHub Actions (managed by the base workspace)"
  type        = string
  default     = ""
}

variable "managed_by_github_actions" {
  description = "If true, GitHub actions will have permissions to change the resources"
  type        = bool
  default     = false
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}
