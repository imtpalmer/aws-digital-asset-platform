
output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.react_app_cloudfront_distribution.id
}

output "cloudfront_distribution_url" {
  value = aws_cloudfront_distribution.react_app_cloudfront_distribution.domain_name
}

output "cloudfront_distribution_arn" {
  value = aws_cloudfront_distribution.react_app_cloudfront_distribution.arn
}