output "cdn_url" {
  description = "CDN domain name"
  value       = aws_cloudfront_distribution.useyourai_ui_cdn.domain_name
}

output "cdn_distribution_id" {
  description = "CDN distribution id"
  value       = aws_cloudfront_distribution.useyourai_ui_cdn.id
}

output "ui_bucket_name" {
  description = "Name of the S3 bucket where UI is hosted"
  value       = aws_s3_bucket.ui_bucket.bucket
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions"
  value       = aws_iam_role.github_actions[*].arn
}
