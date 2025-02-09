module "dynamodb" {
  source  = "../modules/dynamodb"

  environment = var.environment  
}

module "lambdas" {
  source = "../modules/lambdas"

  account_id  = var.account_id
  environment = var.environment
  region      = var.region
}
