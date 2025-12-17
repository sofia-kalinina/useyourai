output "hosted_zone_id" {
  description = "ID of the primary hosted zone"
  value       = aws_route53_zone.primary.id
}

output "nameservers" {
  description = "Nameservers of the hosted zone"
  value       = aws_route53_zone.primary.name_servers
}
