
resource "random_id" "bucket_suffix" {
  byte_length = 8
}

resource "aws_s3_bucket" "ui_bucket" {
  bucket = "useyourai-ui-${var.environment}-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "useyourai-ui-${var.environment}-bucket"
    Environment = "${var.environment}"

  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ui_bucket_encryption" {
  bucket = aws_s3_bucket.ui_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_cloudfront_origin_access_control" "useyourai_ui_oac" {
  name                              = "useyouai-${var.environment}-oac"
  description                       = "OAC for useyourai ui ${var.environment}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "useyourai_ui_cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CDN for useyourai ui ${var.environment}"
  default_root_object = "index.html"

  # We do NOT use 'aliases' since we don't have a custom domain yet

  origin {
    domain_name              = aws_s3_bucket.ui_bucket.bucket_regional_domain_name
    origin_id                = aws_s3_bucket.ui_bucket.id
    origin_access_control_id = aws_cloudfront_origin_access_control.useyourai_ui_oac.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = aws_s3_bucket.ui_bucket.id
    viewer_protocol_policy = "redirect-to-https" # Force HTTPS

    # These settings are good for caching static assets
    min_ttl     = 0
    default_ttl = 86400    # 1 day
    max_ttl     = 31536000 # 1 year

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  # SSL/TLS Certificate
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  # US, Canada, Europe, and Israel
  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none" # No geographic restrictions
    }
  }

  # If the route doesn’t exist (403 or 404), just serve index.html so React Router can take over.
  custom_error_response {
    error_code            = 403 # S3 returns this for private objects
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }
}

# only cloudfront distribution can access the ui bucket
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.ui_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json

  depends_on = [aws_cloudfront_distribution.useyourai_ui_cdn]
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.ui_bucket.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.cdn.arn]
    }
  }
}
