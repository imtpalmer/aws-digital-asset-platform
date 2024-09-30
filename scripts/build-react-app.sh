#!/bin/bash

set -e  # Exit on any error

REACT_APP_DIR="../react-app"
INFRA="../infra"
EXPECTED_DIR="scripts"

# Function to check if script is run from the expected directory
check_directory() {
  CURRENT_DIR=$(basename "$PWD")
  if [ "$CURRENT_DIR" != "$EXPECTED_DIR" ]; then
    echo "Script is NOT running from the $EXPECTED_DIR directory. Exiting."
    exit 1
  fi
  echo "Script is running from the $EXPECTED_DIR directory."
}

# Function to fetch API endpoint from Terraform output
fetch_api_endpoint() {
  echo "Fetching API endpoint from Terraform..."
  API_END_POINT=$(cd "$INFRA" && terraform output -raw api_gateway_v2_url 2>&1)

  if [[ $API_END_POINT == *"No outputs found"* || -z $API_END_POINT ]]; then
    echo "Error: No outputs found for api_gateway_v2_url or the output is empty."
    exit 1
  fi

  echo "API Endpoint is set to: $API_END_POINT"
}

# Function to fetch S3 bucket name for React app hosting
fetch_s3_bucket() {
  echo "Fetching S3 bucket name for React app hosting..."
  REACT_APP_S3_BUCKET=$(cd "$INFRA" && terraform output -raw react_app_s3_bucket 2>&1)

  if [[ $REACT_APP_S3_BUCKET == *"No outputs found"* || -z $REACT_APP_S3_BUCKET ]]; then
    echo "Error: No outputs found for react_app_s3_bucket or the output is empty."
    exit 1
  fi

  echo "S3 Bucket for React app is set to: $REACT_APP_S3_BUCKET"
}

# Function to fetch CloudFront distribution ID
fetch_cloudfront_distribution_id() {
  echo "Fetching CloudFront distribution ID from Terraform..."
  CLOUDFRONT_DISTRIBUTION_ID=$(cd "$INFRA" && terraform output -raw cloudfront_distribution_id 2>&1)

  if [[ $CLOUDFRONT_DISTRIBUTION_ID == *"No outputs found"* || -z $CLOUDFRONT_DISTRIBUTION_ID ]]; then
    echo "Error: No outputs found for cloudfront_distribution_id or the output is empty."
    exit 1
  fi

  echo "CloudFront Distribution ID is set to: $CLOUDFRONT_DISTRIBUTION_ID"
}

# Function to build the React app
build_react_app() {
  echo "Cleaning up React app directories and files..."
  cd "$REACT_APP_DIR"
  rm -rf node_modules build/static build/*.{html,txt,png,ico,json}

  echo "Installing dependencies..."
  # npm install react-scripts --save
  # npm install @reduxjs/toolkit react-redux react-router-dom@latest axios jwt-decode
  npm install

  echo "Building React app..."
  npm run build
  echo "React app built successfully."
}

# Function to upload build files to S3 bucket
upload_to_s3() {
  echo "Uploading build files to S3 bucket: $REACT_APP_S3_BUCKET"
  
  # Ensure the AWS CLI is available and authenticated
  if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install and configure AWS CLI."
    exit 1
  fi

  # Sync the build folder to the S3 bucket
  aws s3 sync build/ "s3://$REACT_APP_S3_BUCKET" --delete

  echo "Build files uploaded to S3 successfully."
}

# Function to invalidate CloudFront cache
invalidate_cloudfront_cache() {
  echo "Creating CloudFront cache invalidation request for distribution ID: $CLOUDFRONT_DISTRIBUTION_ID"
  
  # Invalidate all files from the CloudFront distribution cache
  INVALIDATION_ID=$(aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" --paths "/*" --query 'Invalidation.Id' --output text)

  if [[ -z $INVALIDATION_ID ]]; then
    echo "Error: Failed to create CloudFront cache invalidation."
    exit 1
  fi

  echo "CloudFront cache invalidation created with ID: $INVALIDATION_ID"
}

# Main script execution
# check_directory
fetch_api_endpoint

# Create .env file with API endpoint for the React app
echo "REACT_APP_API_BASE_URL=${API_END_POINT}/dev" > "$REACT_APP_DIR/.env"
echo ".env file created with API endpoint."

# Build the React app
build_react_app

# Fetch S3 bucket name and upload build files
fetch_s3_bucket
upload_to_s3

# Fetch CloudFront distribution ID and invalidate cache
fetch_cloudfront_distribution_id
invalidate_cloudfront_cache

exit 0