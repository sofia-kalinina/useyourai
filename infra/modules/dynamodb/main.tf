resource "aws_dynamodb_table" "language_learning" {
  name         = "LanguageLearningTable-${var.environment}"
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
    name = "ttl"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  global_secondary_index {
    name            = "TTLIndex"
    hash_key        = "ttl"
    projection_type = "ALL"
  }
}
