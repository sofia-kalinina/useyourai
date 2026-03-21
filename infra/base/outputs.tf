output "prod_certificate_arn" {
  description = "ARN of the validated certificate for the prod environment"
  value       = var.create_certificate ? aws_acm_certificate_validation.prod_certificate_validation[0].certificate_arn : null
}

output "dev_certificate_arn" {
  description = "ARN of the validated certificate for the dev environment"
  value       = var.create_certificate ? aws_acm_certificate_validation.dev_certificate_validation[0].certificate_arn : null
}

output "hosted_zone_id" {
  description = "ID of the primary hosted zone"
  value       = aws_route53_zone.primary.id
}

output "nameservers" {
  description = "Nameservers of the hosted zone"
  value       = aws_route53_zone.primary.name_servers
}
