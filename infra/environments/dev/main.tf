module "dynamodb" {
  source = "../../modules/dynamodb"

  environment = var.environment
}

module "lambdas" {
  source = "../../modules/lambdas"

  account_id  = var.account_id
  environment = var.environment
  region      = var.region
}

module "api_gateway" {
  source = "../../modules/api_gateway"

  environment = var.environment
  lambdas = [
    {
      name       = module.lambdas.init_session_lambda_name
      invoke_arn = module.lambdas.init_session_lambda_invoke_arn
      route_key  = "POST /init"
    },
    {
      name       = module.lambdas.test_bedrock_lambda_name
      invoke_arn = module.lambdas.test_bedrock_lambda_invoke_arn
      route_key  = "POST /test"
    }
  ]
}

module "ui" {
  source = "../../modules/ui"

  environment = var.environment
}
