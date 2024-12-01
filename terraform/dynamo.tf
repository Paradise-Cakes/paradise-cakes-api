resource "aws_dynamodb_table" "desserts" {
  name         = "desserts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "dessert_id"

  attribute {
    name = "dessert_id"
    type = "S"
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

  attribute {
    name = "scheduled_delivery_time"
    type = "S"
  }

  global_secondary_index {
    name               = "scheduled_delivery_time_index"
    hash_key           = "scheduled_delivery_time"
    projection_type    = "ALL"
    read_capacity      = 5
    write_capacity     = 5
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
