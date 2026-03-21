# The GitHub OIDC provider already exists in AWS (created by the dev frontend module).
# Read it as a data source — it is account-global and needs no further management.
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

# Import the existing role from dev's state into base so it is managed here.
import {
  to = aws_iam_role.github_actions
  id = "useyourai-github-actions-role"
}

resource "aws_iam_role" "github_actions" {
  name = "useyourai-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
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
