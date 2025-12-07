output "api_gateway_invoke_url" {
  value = module.api_gateway.api_gateway_invoke_url
}

output "cdn_distribution_id" {
  value = module.ui.cdn_distribution_id
}

output "cdn_url" {
  value = module.ui.cdn_url
}

output "ui_bucket_name" {
  value = module.ui.ui_bucket_name
}
