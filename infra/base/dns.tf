resource "aws_route53_zone" "primary" {
  name = "useyourai.eu"

  tags = local.common_tags
}
