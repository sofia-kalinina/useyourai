provider "aws" {
  region = var.region
}

provider "tfe" {
  # Token is provided automatically by TFC at runtime
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
