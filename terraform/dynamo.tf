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

  attribute {
    name = "last_updated"
    type = "N"
  }

  global_secondary_index {
    name            = "dessert_type_index"
    hash_key        = "dessert_type"
    range_key       = "last_updated"
    projection_type = "ALL"
  }
}

resource "aws_dynamodb_table" "dessert_type_count" {
  name         = "dessert_type_count"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "dessert_type"

  attribute {
    name = "dessert_type"
    type = "S"
  }
}

data "aws_dynamodb_table" "dessert_type_count_created" {
  name       = "dessert_type_count"
  depends_on = [aws_dynamodb_table.dessert_type_count]
}

resource "aws_dynamodb_table" "prices" {
  name         = "prices"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "dessert_id"
  range_key    = "size"

  attribute {
    name = "dessert_id"
    type = "S"
  }

  attribute {
    name = "size"
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
    name = "delivery_date"
    type = "S"
  }

  attribute {
    name = "delivery_time"
    type = "N"
  }

  attribute {
    name = "customer_full_name"
    type = "S"
  }

  attribute {
    name = "order_date"
    type = "S"
  }

  attribute {
    name = "order_time"
    type = "N"
  }

  # get me all the orders for a specific delivery date and sort them by when they need to be delivered
  global_secondary_index {
    name            = "delivery_date_index"
    hash_key        = "delivery_date"
    range_key       = "delivery_time"
    projection_type = "ALL"
  }

  # get me all the orders for a specific customer and sort them by when they were placed
  global_secondary_index {
    name            = "customer_full_name_index"
    hash_key        = "customer_full_name"
    range_key       = "order_time"
    projection_type = "ALL"
  }

  # get me all the orders for a specific order date and sort them by when they were placed
  global_secondary_index {
    name            = "order_date_index"
    hash_key        = "order_date"
    range_key       = "order_time"
    projection_type = "ALL"
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
