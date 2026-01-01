variable "cdn_url" {
  description = "CDN url"
  type        = string
}

variable "custom_domain_name" {
  description = "Custom domain name for CORS"
  type        = string
  default     = ""
}

variable "common_tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
}

variable "environment" {
  description = "The environment name"
  type        = string
}

variable "lambdas" {
  description = "The list of lambdas to integrate with the API Gateway"
  type = list(object({
    name       = string
    invoke_arn = string
    route_key  = string
  }))
}

variable "project_name" {
  description = "The name of the project"
  type        = string
}
