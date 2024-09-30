# CloudFront Distribution OAC
resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "react-app-oac"
  description                       = "OAC for React App"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "react_app_cloudfront_distribution" {

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for React App"
  default_root_object = "index.html"

  origin {
    domain_name              = var.react_bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
    origin_id                = "S3Origin" # Descriptive string, not a variable
  }
  default_cache_behavior {
    allowed_methods  = ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"

    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400

    response_headers_policy_id = aws_cloudfront_response_headers_policy.react_app_cors_policy.id
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# Response Headers Policy (CORS + Security)
resource "aws_cloudfront_response_headers_policy" "react_app_cors_policy" {
  name = "digital_assets_react_cors_policy"

  cors_config {
    access_control_allow_credentials = false

    access_control_allow_headers {
      items = ["*"]
    }

    access_control_allow_methods {
      items = ["GET", "HEAD", "OPTIONS", "PUT", "POST"] # Include POST
      # items = ["GET", "HEAD", "OPTIONS"]  # Limited to typical CORS-safe methods
    }

    access_control_allow_origins {
      items = ["*"] # Adjust this if you want stricter control
    }

    access_control_expose_headers {
      items = ["*"]
    }

    access_control_max_age_sec = 600
    origin_override            = true
  }

  security_headers_config {
    content_security_policy {
      override                = true
      # content_security_policy = "default-src 'self'; connect-src 'self' https://*.cloudfront.net https://*.execute-api.us-east-1.amazonaws.com https://*.s3.amazonaws.com; img-src 'self'; script-src 'self'; style-src 'self';"
      content_security_policy = "default-src 'self'; connect-src 'self' https://*.cloudfront.net https://*.execute-api.us-east-1.amazonaws.com https://*.s3.amazonaws.com;"
    }
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    referrer_policy {
      referrer_policy = "no-referrer"
      override        = true
    }
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true
    }
    xss_protection {
      protection = true
      mode_block = true
      override   = true
    }
  }
}