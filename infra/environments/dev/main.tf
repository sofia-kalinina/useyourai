data "tfe_outputs" "base_outputs" {
  organization = "sofiia-kalinina"
  workspace    = "useyourai-base"
}

locals {
  project_name = var.project_name
  common_tags = {
    Project     = local.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  name_prefix = "${local.project_name}-${var.environment}"
}

module "frontend" {
  source = "../../modules/frontend"
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  common_tags     = local.common_tags
  domain_name     = "dev.${var.domain_name}"
  environment     = var.environment
  hosted_zone_id  = data.tfe_outputs.base_outputs.values.hosted_zone_id
  certificate_arn = data.tfe_outputs.base_outputs.values.dev_certificate_arn
  project_name    = var.project_name

  managed_by_github_actions = true

}

module "dynamodb" {
  source = "../../modules/dynamodb"

  environment  = var.environment
  project_name = var.project_name
  common_tags  = local.common_tags
}

module "lambdas" {
  source = "../../modules/lambdas"

  account_id          = var.account_id
  environment         = var.environment
  region              = var.region
  project_name        = var.project_name
  common_tags         = local.common_tags
  dynamodb_table_name = module.dynamodb.table_name
  dynamodb_table_arn  = module.dynamodb.table_arn
}

module "api_gateway" {
  source = "../../modules/api_gateway"

  environment        = var.environment
  project_name       = var.project_name
  common_tags        = local.common_tags
  cdn_url            = module.frontend.cdn_url
  custom_domain_name = "dev.${var.domain_name}"

  lambdas = [
    {
      name       = module.lambdas.create_session_lambda_name
      invoke_arn = module.lambdas.create_session_lambda_invoke_arn
      route_key  = "POST /session"
    },
    {
      name       = module.lambdas.submit_answer_lambda_name
      invoke_arn = module.lambdas.submit_answer_lambda_invoke_arn
      route_key  = "POST /session/{id}/answer"
    },
    {
      name       = module.lambdas.retry_session_lambda_name
      invoke_arn = module.lambdas.retry_session_lambda_invoke_arn
      route_key  = "POST /session/{id}/retry"
    },
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
