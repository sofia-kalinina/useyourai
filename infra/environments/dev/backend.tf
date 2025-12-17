terraform {
  cloud {
    organization = "sofiia-kalinina"

    workspaces {
      name = "useyourai-dev"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.20"
    }
  }
}
