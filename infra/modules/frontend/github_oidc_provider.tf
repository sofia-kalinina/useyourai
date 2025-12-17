## TODO: extend to work with prod env, possibly move to a separate module

resource "aws_iam_openid_connect_provider" "github" {
  count = var.managed_by_github_actions ? 1 : 0
  url   = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]

  tags = {
    Name = "GitHub Actions OIDC"
  }
}

resource "aws_iam_role" "github_actions" {
  count = var.managed_by_github_actions ? 1 : 0
  name  = "useyourai-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github[count.index].arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:sofia-kalinina/useyourai:ref:refs/heads/main",
              "repo:sofia-kalinina/useyourai:pull_request"
            ]
          }
        }
      }
    ]
  })

  tags = {
    Purpose = "GitHub Actions deployment"
  }
}

resource "aws_iam_policy" "github_deploy" {
  count       = var.managed_by_github_actions ? 1 : 0
  name        = "useyourai-repo-github-deploy-policy"
  description = "Allow S3 deployment and CloudFront invalidation"

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
  role       = aws_iam_role.github_actions[count.index].name
  policy_arn = aws_iam_policy.github_deploy[count.index].arn
}
