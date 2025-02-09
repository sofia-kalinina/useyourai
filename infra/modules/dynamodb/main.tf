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

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name        = "LanguageLearningTable-${var.environment}"
    Environment = "${var.environment}"
  }
}
