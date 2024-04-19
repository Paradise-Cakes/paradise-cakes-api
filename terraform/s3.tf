resource "aws_s3_bucket" "pc_dessert_images_bucket" {
  bucket = "pc-dessert-images-bucket"
}

resource "aws_s3_bucket_cors_configuration" "pc_dessert_images_bucket_cors" {
  bucket = aws_s3_bucket.pc_dessert_images_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }

  cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
  }
}
