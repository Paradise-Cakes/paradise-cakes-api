resource "aws_dynamodb_table" "desserts" {
  name         = "desserts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "dessert_id"

  attribute {
    name = "dessert_id"
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


resource "aws_dynamodb_table" "orders" {
  name         = "orders"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "order_type_count" {
  name         = "order_type_count"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "order_type"

  attribute {
    name = "order_type"
    type = "S"
  }
}

data "aws_dynamodb_table" "order_type_count_created" {
  name       = "order_type_count"
  depends_on = [aws_dynamodb_table.order_type_count]
}


resource "aws_dynamodb_table" "dessert_images" {
  name         = "dessert_images"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "dessert_id"
  range_key    = "image_id"

  attribute {
    name = "dessert_id"
    type = "S"
  }

  attribute {
    name = "image_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "N"
  }

  global_secondary_index {
    name            = "dessert_id_by_created_at_index"
    hash_key        = "dessert_id"
    range_key       = "created_at"
    projection_type = "ALL"
  }
}
