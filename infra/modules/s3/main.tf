# S3 assets bucket for digital assets
resource "aws_s3_bucket" "assets_bucket" {
  bucket = var.digital_assets_bucket_name
  tags = {
    Name        = "DigitalAssetsBucket"
    Environment = "${var.environment}"
  }
}

# Secure the digital assets bucket from public access
resource "aws_s3_bucket_public_access_block" "assets_bucket_public_access_block" {
  bucket = aws_s3_bucket.assets_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

# CORS settings for the digital assets bucket
resource "aws_s3_bucket_cors_configuration" "assets_bucket_cors" {
  bucket = aws_s3_bucket.assets_bucket.id

  cors_rule {
    allowed_headers = ["Authorization", "Content-Type", "x-amz-acl", "x-amz-meta-*"]
    allowed_methods = ["GET", "PUT", "POST"] # Adjust as needed based on your app's needs
    allowed_origins = ["*"]                  # Ideally, restrict this to specific origins
    expose_headers  = ["ETag","Content-Security-Policy","x-amz-acl"] 
    max_age_seconds = 3000
  }
}

/*
# IAM policy for multipart upload to S3
resource "aws_iam_policy" "s3_multipart_upload_policy" {
  name        = "S3MultipartUploadPolicy"
  description = "Allow multipart upload to S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:CreateMultipartUpload",
          "s3:UploadPart",
          "s3:CompleteMultipartUpload",
          "s3:AbortMultipartUpload"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.assets_bucket.arn,
          "${aws_s3_bucket.assets_bucket.arn}/*"
        ]
      }
    ]
  })
}
*/

# Host React App assets in S3
resource "aws_s3_bucket" "react_bucket" {
  bucket = var.digital_assets_react_bucket_name

  tags = {
    Name        = "ReactAppBucket"
    Environment = "${var.environment}"
  }
}

# Block public access to the React app bucket and serve via CloudFront
resource "aws_s3_bucket_public_access_block" "react_bucket_public_access_block" {
  bucket = aws_s3_bucket.react_bucket.id

  block_public_acls  = false # Block any public ACLs (access control lists) from being applied to objects in this bucket.
  ignore_public_acls = true  # Ignore any existing public ACLs that might have been set.
  /* block_public_policy     = true  # Prevent the bucket from having any public policies that allow public access.
  restrict_public_buckets = true  # Restrict the bucket from being made public in any way, either by ACLs or bucket policy. */
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_policy" "react_bucket_policy" {
  bucket = aws_s3_bucket.react_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Id      = "PolicyForCloudFrontPrivateContent",
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal",
        Effect = "Allow",
        Principal = {
          Service = "cloudfront.amazonaws.com"
        },
        Action   = "s3:GetObject",
        Resource = "${aws_s3_bucket.react_bucket.arn}/*",
        Condition = {
          ArnLike = {
            "AWS:SourceArn" : "${var.cloudfront_distribution_arn}"
          },
          StringEquals = {
            "AWS:SourceAccount" : "${data.aws_caller_identity.current.account_id}"
          }
        }
      }
    ]
  })
}

# CORS configuration for the React app bucket
resource "aws_s3_bucket_cors_configuration" "react_bucket_cors" {
  bucket = aws_s3_bucket.react_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT", "POST"]      # Include PUT/POST if you're allowing uploads
    allowed_origins = ["*"]                               # Ideally restrict this to specific origins
    expose_headers  = ["ETag", "Content-Security-Policy"] # Required for multipart upload
    max_age_seconds = 3000
  }
}

# S3 website configuration for React app hosting
resource "aws_s3_bucket_website_configuration" "react_website_config" {
  bucket = aws_s3_bucket.react_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }

  # Uncomment if you want to serve index.html for all 404s to support client-side routing
  # routing_rules = jsonencode([{
  #   Condition = {
  #     HttpErrorCodeReturnedEquals = "404"
  #   }
  #   Redirect = {
  #     ReplaceKeyWith = "index.html"
  #   }
  # }])
}
