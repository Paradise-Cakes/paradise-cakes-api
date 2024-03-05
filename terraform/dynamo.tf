resource "aws_dynamodb_table" "desserts" {
  name         = "desserts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "uid"

  attribute {
    name = "uid"
    type = "S"
  }

  attribute {
    name = "dessert_type"
    type = "S"
  }

  global_secondary_index {
    name            = "dessert-type-index"
    hash_key        = "dessert_type"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }
}
