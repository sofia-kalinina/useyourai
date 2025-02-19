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
