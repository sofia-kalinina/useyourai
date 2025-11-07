terraform {
  cloud {
    organization = "sofiia-kalinina"

    workspaces {
      name = "useyourai-${var.environment}"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.20"
    }
  }
}
