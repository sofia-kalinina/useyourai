provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for provider configuration"
  type        = string
  default     = "eu-central-1"
}