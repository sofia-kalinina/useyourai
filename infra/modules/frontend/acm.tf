
resource "aws_acm_certificate" "frontend_certificate" {
  provider          = aws.us_east_1
  domain            = var.domain_name
  validation_method = "DNS"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-certificate"
  })
}

resource "aws_route53_record" "validation_record" {
  for_each = {
    for dvo in aws_acm_certificate.this.domain_validation_options :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }
  zone_id = var.hosted_zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "frontend_certificate_validation" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.frontend_certificate.arn
  validation_record_fqdns = [aws_route53_record.validation_record.fqdn]
  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-certificate-validation"
  })
}
