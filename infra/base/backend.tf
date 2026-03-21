terraform {
  cloud {
    organization = "sofiia-kalinina"

    workspaces {
      name = "useyourai-base"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.20"
    }
    tfe = {
      source  = "hashicorp/tfe"
      version = ">= 0.58"
    }
  }
}
