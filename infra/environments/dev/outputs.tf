output "api_gateway_url" {
  value = module.api_gateway.api_gateway_url
}

output "cdn_distribution_id" {
  value = module.frontend.cdn_distribution_id
}

output "cdn_url" {
  value = module.frontend.cdn_url
}

output "ui_bucket_name" {
  value = module.frontend.ui_bucket_name
}
