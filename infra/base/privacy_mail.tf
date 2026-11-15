# Receives mail for privacy@<domain> with SES in the main region and forwards it to the
# owner's inbox. SES stores each raw message in S3, then a Lambda reads it and resends it
# from the privacy address, because SES can only send from a verified identity.

locals {
  privacy_address       = "privacy@${var.domain_name}"
  privacy_mail_prefix   = "privacy/"
  inbound_rule_set_name = "${local.name_prefix}-inbound"
  privacy_rule_name     = "forward-privacy"
  privacy_rule_arn      = "arn:aws:ses:${var.region}:${var.account_id}:receipt-rule-set/${local.inbound_rule_set_name}:receipt-rule/${local.privacy_rule_name}"
}

# Domain identity, so SES accepts mail for the domain and can send from the privacy address

resource "aws_ses_domain_identity" "primary" {
  domain = var.domain_name
}

resource "aws_route53_record" "ses_verification" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "_amazonses.${var.domain_name}"
  type    = "TXT"
  ttl     = 600
  records = [aws_ses_domain_identity.primary.verification_token]
}

resource "aws_ses_domain_identity_verification" "primary" {
  domain = aws_ses_domain_identity.primary.id

  depends_on = [aws_route53_record.ses_verification]
}

# DKIM signs the forwarded mail as the domain, so the owner's provider does not mark it as spam
resource "aws_ses_domain_dkim" "primary" {
  domain = aws_ses_domain_identity.primary.domain
}

resource "aws_route53_record" "ses_dkim" {
  count   = 3
  zone_id = aws_route53_zone.primary.zone_id
  name    = "${aws_ses_domain_dkim.primary.dkim_tokens[count.index]}._domainkey.${var.domain_name}"
  type    = "CNAME"
  ttl     = 600
  records = ["${aws_ses_domain_dkim.primary.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = var.domain_name
  type    = "MX"
  ttl     = 600
  records = ["10 inbound-smtp.${var.region}.amazonaws.com"]
}

# While the account is in the SES sandbox, it can only send to verified addresses.
# AWS emails a verification link to this address after the first apply.
resource "aws_ses_email_identity" "privacy_forward_to" {
  email = var.privacy_forward_to_email
}

# Raw messages, kept long enough to recover one if forwarding fails

resource "aws_s3_bucket" "privacy_mail" {
  bucket = "${local.name_prefix}-privacy-mail-${var.account_id}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-privacy-mail"
  })
}

resource "aws_s3_bucket_public_access_block" "privacy_mail" {
  bucket = aws_s3_bucket.privacy_mail.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "privacy_mail" {
  bucket = aws_s3_bucket.privacy_mail.id

  rule {
    blocked_encryption_types = ["SSE-C"]

    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "privacy_mail" {
  bucket = aws_s3_bucket.privacy_mail.id

  rule {
    id     = "expire-privacy-mail"
    status = "Enabled"

    filter {}

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_policy" "privacy_mail" {
  bucket = aws_s3_bucket.privacy_mail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowSESPuts"
        Effect    = "Allow"
        Principal = { Service = "ses.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.privacy_mail.arn}/${local.privacy_mail_prefix}*"
        Condition = {
          StringEquals = { "AWS:SourceAccount" = var.account_id }
          ArnLike      = { "AWS:SourceArn" = local.privacy_rule_arn }
        }
      }
    ]
  })
}

# Forwarding Lambda

data "archive_file" "forward_privacy_email_lambda" {
  type        = "zip"
  source_file = "../../lambdas/forward_privacy_email.py"

  output_path = "forward_privacy_email.zip"
}

resource "aws_iam_role" "forward_privacy_email" {
  name = "${local.name_prefix}-forward-privacy-email-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      },
    ]
  })
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "forward_privacy_email_logs" {
  role       = aws_iam_role.forward_privacy_email.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "forward_privacy_email" {
  name = "${local.name_prefix}-forward-privacy-email-policy"
  role = aws_iam_role.forward_privacy_email.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "s3:GetObject"
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.privacy_mail.arn}/${local.privacy_mail_prefix}*"
      },
      {
        # In the SES sandbox, sending is also authorised against the recipient's identity
        Action   = "ses:SendRawEmail"
        Effect   = "Allow"
        Resource = [aws_ses_domain_identity.primary.arn, aws_ses_email_identity.privacy_forward_to.arn]
      }
    ]
  })
}

resource "aws_lambda_function" "forward_privacy_email" {
  filename      = "forward_privacy_email.zip"
  function_name = "${local.name_prefix}-lambda-forward-privacy-email"
  role          = aws_iam_role.forward_privacy_email.arn
  handler       = "forward_privacy_email.lambda_handler"
  timeout       = 30
  memory_size   = 256

  source_code_hash = data.archive_file.forward_privacy_email_lambda.output_base64sha256

  runtime = "python3.14"

  environment {
    variables = {
      MAIL_BUCKET = aws_s3_bucket.privacy_mail.id
      MAIL_PREFIX = local.privacy_mail_prefix
      SENDER      = local.privacy_address
      FORWARD_TO  = var.privacy_forward_to_email
    }
  }
  tags = local.common_tags
}

resource "aws_lambda_permission" "forward_privacy_email_ses" {
  statement_id   = "AllowExecutionFromSES"
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.forward_privacy_email.function_name
  principal      = "ses.amazonaws.com"
  source_account = var.account_id
  source_arn     = local.privacy_rule_arn
}

# Receipt rules. Only one rule set can be active per region, and this is it.

resource "aws_ses_receipt_rule_set" "inbound" {
  rule_set_name = local.inbound_rule_set_name
}

resource "aws_ses_active_receipt_rule_set" "inbound" {
  rule_set_name = aws_ses_receipt_rule_set.inbound.rule_set_name
}

resource "aws_ses_receipt_rule" "forward_privacy" {
  name          = local.privacy_rule_name
  rule_set_name = aws_ses_receipt_rule_set.inbound.rule_set_name
  recipients    = [local.privacy_address]
  enabled       = true
  scan_enabled  = true

  s3_action {
    bucket_name       = aws_s3_bucket.privacy_mail.id
    object_key_prefix = local.privacy_mail_prefix
    position          = 1
  }

  lambda_action {
    function_arn    = aws_lambda_function.forward_privacy_email.arn
    invocation_type = "Event"
    position        = 2
  }

  # SES checks both permissions when the rule is created
  depends_on = [aws_s3_bucket_policy.privacy_mail, aws_lambda_permission.forward_privacy_email_ses]
}
