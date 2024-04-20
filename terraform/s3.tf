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

resource "aws_s3_bucket_public_access_block" "pc_dessert_images_bucket_pab" {
  bucket = aws_s3_bucket.pc_dessert_images_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

data "aws_iam_policy_document" "dessert_images_bucket_policy" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
    resources = [aws_s3_bucket.pc_dessert_images_bucket.arn, "${aws_s3_bucket.pc_dessert_images_bucket.arn}/*"]
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

resource "aws_s3_bucket_policy" "pc_dessert_images_bucket_policy" {
  bucket = aws_s3_bucket.pc_dessert_images_bucket.id
  policy = data.aws_iam_policy_document.dessert_images_bucket_policy.json
  depends_on = [aws_s3_bucket_public_access_block.pc_dessert_images_bucket_pab]
}
