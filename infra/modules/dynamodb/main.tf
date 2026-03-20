resource "aws_dynamodb_table" "language_learning" {
  name         = "${var.project_name}-${var.environment}-table-language-learning"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "session_id"
  range_key = "question_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "question_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "by-user"
    hash_key        = "user_id"
    range_key       = "session_id"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-table-language-learning"
  })
}
