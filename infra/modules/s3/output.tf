output "react_bucket_arn" {
  value = aws_s3_bucket.react_bucket.arn
}

output "react_bucket_regional_domain_name" {
  # value = aws_s3_bucket.react_bucket.bucket_domain_name
  value = aws_s3_bucket.react_bucket.bucket_regional_domain_name
}

output "react_bucket_bucket" {
  value = aws_s3_bucket.react_bucket.bucket
}

output "react_bucket_bucket_id" {
  value = aws_s3_bucket.react_bucket.id
}