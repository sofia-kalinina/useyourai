
resource "aws_acm_certificate" "prod_certificate" {
  count             = var.create_certificate ? 1 : 0
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  validation_method = "DNS"

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-prod-certificate"
  })
}

resource "aws_route53_record" "prod_certificate_validation_record" {
  for_each = {
    for dvo in var.create_certificate ? aws_acm_certificate.prod_certificate[0].domain_validation_options : [] :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }
  allow_overwrite = true
  zone_id         = aws_route53_zone.primary.zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 60
}

resource "aws_acm_certificate_validation" "prod_certificate_validation" {
  count                   = var.create_certificate ? 1 : 0
  provider                = aws.us_east_1
  certificate_arn         = element(concat(aws_acm_certificate.prod_certificate.*.arn, [""]), 0)
  validation_record_fqdns = [for record in aws_route53_record.prod_certificate_validation_record : record.fqdn]

  depends_on = [aws_route53_record.prod_certificate_validation_record]

  timeouts {
    create = "45m"
  }
}

resource "aws_acm_certificate" "dev_certificate" {
  count             = var.create_certificate ? 1 : 0
  provider          = aws.us_east_1
  domain_name       = "dev.${var.domain_name}"
  validation_method = "DNS"

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-dev-certificate"
  })
}

resource "aws_route53_record" "dev_certificate_validation_record" {
  for_each = {
    for dvo in var.create_certificate ? aws_acm_certificate.dev_certificate[0].domain_validation_options : [] :
    dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }
  allow_overwrite = true
  zone_id         = aws_route53_zone.primary.zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 60
}

resource "aws_acm_certificate_validation" "dev_certificate_validation" {
  count                   = var.create_certificate ? 1 : 0
  provider                = aws.us_east_1
  certificate_arn         = element(concat(aws_acm_certificate.dev_certificate.*.arn, [""]), 0)
  validation_record_fqdns = [for record in aws_route53_record.dev_certificate_validation_record : record.fqdn]

  depends_on = [aws_route53_record.dev_certificate_validation_record]

  timeouts {
    create = "45m"
  }
}
