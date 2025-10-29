terraform {
  cloud {
    organization = "sofiia-kalinina"

    workspaces {
      name = "useyourai-${var.environment}"
    }
  }
}