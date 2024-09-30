#!/bin/bash

set -e

# Define the directory containing your Terraform configuration
TERRAFORM_DIR="../infra"

# Function to retrieve Terraform output in JSON format
get_terraform_output_json() {
  local output_name=$1
  terraform -chdir="$TERRAFORM_DIR" output -json "$output_name"
}

# Function to send CORS preflight request
send_cors_preflight() {
  local endpoint=$1
  local cloudfront_url=$2

  local headers=(
    -H "Access-Control-Request-Method: POST"
    -H "Access-Control-Request-Headers: Authorization, Content-Type"
    -H "Origin: $cloudfront_url"
  )

  echo -e "\nSending CORS preflight request to $endpoint..."
  local response
  response=$(curl -X OPTIONS "${headers[@]}" -i "$endpoint" 2>/dev/null)

  if [[ $? -eq 0 ]]; then
    echo -e "Response from $endpoint:\n$response"
  else
    echo "Error: Failed to send OPTIONS request to $endpoint."
  fi
}

# Retrieve the CloudFront URL using Terraform output
CLOUDFRONT_URL=$(terraform -chdir="$TERRAFORM_DIR" output -raw "react_app_url")

# Check if the CloudFront URL was successfully retrieved
if [[ -z "$CLOUDFRONT_URL" ]]; then
  echo "Error: Failed to retrieve CloudFront URL."
  exit 1
fi

echo "CloudFront URL: $CLOUDFRONT_URL"

# Retrieve the API Gateway URLs in JSON format
API_GATEWAY_URLS=$(terraform -chdir="$TERRAFORM_DIR" output -json "api_gateway_v2_urls")

# Retrieve the API Gateway Routes in JSON format
ROUTES=$(get_terraform_output_json "api_gateway_routes")

# Check if the output for API Gateway Routes is valid JSON
if [[ -z "$ROUTES" || "$(echo "$ROUTES" | jq -r 'type')" != "array" ]]; then
  echo "Error: API Gateway Routes output is either empty or not valid JSON."
  exit 1
fi

# Handle both cases for API Gateway URLs (string or list)
if [[ $(echo "$API_GATEWAY_URLS" | jq -r 'type') == "string" ]]; then
  API_GATEWAY_URLS=$(echo "$API_GATEWAY_URLS" | jq -r '.')
else
  API_GATEWAY_URLS=$(echo "$API_GATEWAY_URLS" | jq -r '.[]')
fi

# Loop through each API Gateway URL
for api_gateway_url in $API_GATEWAY_URLS; do
  echo -e "\nChecking API Gateway URL: $api_gateway_url"

  # Loop through each route
  echo "$ROUTES" | jq -c '.[]' | while read -r route; do
    route_key=$(echo "$route" | jq -r '.route_key')
    http_method=$(echo "$route" | jq -r '.http_method')

    # Extract the path from the route_key (ignoring the HTTP method)
    path=$(echo "$route_key" | cut -d' ' -f2)

    # Check if the route has OPTIONS method
    if [[ "$http_method" == "OPTIONS" ]]; then
      endpoint="$api_gateway_url/dev$path"
      send_cors_preflight "$endpoint" "$CLOUDFRONT_URL"
    fi
  done
done