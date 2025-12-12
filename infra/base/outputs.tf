output "nameservers" {
  description = "Nameservers of the hosted zone"
  value       = aws_route53_zone.primary.name_servers
}
