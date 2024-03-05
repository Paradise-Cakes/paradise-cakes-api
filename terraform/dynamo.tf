resource "aws_dynamodb_table" "desserts" {
  name         = "desserts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "uid"

  attribute {
    name = "uid"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  global_secondary_index {
    name            = "type-index"
    hash_key        = "type"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }
}
