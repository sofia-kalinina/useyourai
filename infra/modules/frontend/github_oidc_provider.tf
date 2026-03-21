# The OIDC provider and shared IAM role are account-global resources managed by
# the base workspace. Remove them from per-environment state without destroying
# the underlying AWS resources.
removed {
  from = aws_iam_openid_connect_provider.github
  lifecycle {
    destroy = false
  }
}

removed {
  from = aws_iam_role.github_actions
  lifecycle {
    destroy = false
  }
}

resource "aws_iam_policy" "github_deploy" {
  count       = var.managed_by_github_actions ? 1 : 0
  name        = "${var.project_name}-${var.environment}-github-deploy-policy"
  description = "Allow S3 deployment and CloudFront invalidation for ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3DeploymentAccess"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.frontend_bucket.arn,
          "${aws_s3_bucket.frontend_bucket.arn}/*"
        ]
      },
      {
        Sid    = "CloudFrontInvalidation"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation"
        ]
        Resource = aws_cloudfront_distribution.frontend_cdn.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_deploy" {
  count      = var.managed_by_github_actions ? 1 : 0
  role       = var.github_actions_role_name
  policy_arn = aws_iam_policy.github_deploy[0].arn
}
