locals {
  project_name = var.project_name
  common_tags = {
    Project     = local.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  name_prefix = "${local.project_name}-${var.environment}"
}

module "ui" {
  source = "../../modules/ui"

  environment               = var.environment
  project_name              = var.project_name
  managed_by_github_actions = true
  common_tags               = local.common_tags
}

module "dynamodb" {
  source = "../../modules/dynamodb"

  environment  = var.environment
  project_name = var.project_name
  common_tags  = local.common_tags
}

module "lambdas" {
  source = "../../modules/lambdas"

  account_id   = var.account_id
  environment  = var.environment
  region       = var.region
  project_name = var.project_name
  common_tags  = local.common_tags
}

module "api_gateway" {
  source = "../../modules/api_gateway"

  environment  = var.environment
  project_name = var.project_name
  common_tags  = local.common_tags
  cdn_url      = module.ui.cdn_url
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

