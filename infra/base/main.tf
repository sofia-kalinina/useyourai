locals {
  project_name = var.project_name
  common_tags = {
    Project     = local.project_name
    Environment = "base"
    ManagedBy   = "Terraform"
  }
  name_prefix = "${local.project_name}-base"
}
