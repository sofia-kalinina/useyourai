resource "aws_dynamodb_table" "language_learning" {
  name         = "${var.project_name}-${var.environment}-table-language-learning"
  billing_mode = "PAY_PER_REQUEST"

  key_schema {
    attribute_name = "session_id"
    key_type       = "HASH"
  }

  key_schema {
    attribute_name = "question_id"
    key_type       = "RANGE"
  }

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
    projection_type = "ALL"

    key_schema {
      attribute_name = "user_id"
      key_type       = "HASH"
    }

    key_schema {
      attribute_name = "session_id"
      key_type       = "RANGE"
    }
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-${var.environment}-table-language-learning"
  })
}
