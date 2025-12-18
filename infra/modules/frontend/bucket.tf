resource "random_id" "bucket_suffix" {
  byte_length = 8
}

resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "${var.project_name}-${var.environment}-ui-bucket-${random_id.bucket_suffix.hex}"

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-ui-bucket"
  })
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend_bucket_encryption" {
  bucket = aws_s3_bucket.frontend_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}


# only cloudfront distribution can access the ui bucket
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.frontend_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json

  depends_on = [aws_cloudfront_distribution.frontend_cdn]
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.frontend_bucket.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.frontend_cdn.arn]
    }
  }
}
