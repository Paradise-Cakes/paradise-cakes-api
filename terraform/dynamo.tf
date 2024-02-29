resource "aws_dynamodb_table" "desserts" {
    name = "desserts"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "uid"

    attribute {
        name = "uid"
        type = "S"
    }
    attribute {
        name = "created"
        type = "N"
    }
    attribute {
        name = "last_updated"
        type = "N"
    }
}