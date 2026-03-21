output "cdn_url" {
  description = "CDN domain name"
  value       = aws_cloudfront_distribution.frontend_cdn.domain_name
}

output "cdn_distribution_id" {
  description = "CDN distribution id"
  value       = aws_cloudfront_distribution.frontend_cdn.id
}

output "ui_bucket_name" {
  description = "Name of the S3 bucket where UI is hosted"
  value       = aws_s3_bucket.frontend_bucket.bucket
}

