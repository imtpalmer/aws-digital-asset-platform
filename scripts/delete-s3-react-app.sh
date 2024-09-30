#!/bin/bash

set -e  # Exit on any error

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

# Function to fetch S3 bucket name for React app hosting
fetch_s3_bucket() {
  echo "Fetching S3 bucket name for React app hosting..."
  REACT_APP_S3_BUCKET=$(cd "$INFRA" && terraform output -raw react_app_s3_bucket 2>&1)
  echo $REACT_APP_S3_BUCKET

  if [[ $REACT_APP_S3_BUCKET == *"No outputs found"* || -z $REACT_APP_S3_BUCKET ]]; then
    echo "Error: No outputs found for react_app_s3_bucket or the output is empty."
    exit 1
  fi

  echo "S3 Bucket for React app is set to: $REACT_APP_S3_BUCKET"
}

# Function to delete the React app assets from S3 bucket
delete_from_s3() {
  echo "Deleting React app assets from S3 bucket: $REACT_APP_S3_BUCKET"
  
  # Ensure the AWS CLI is available and authenticated
  if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install and configure AWS CLI."
    exit 1
  fi

  # Sync the build folder to the S3 bucket and delete files
  aws s3 rm "s3://$REACT_APP_S3_BUCKET" --recursive

  echo "React app assets deleted from S3 successfully."
}

# Main script execution
check_directory

# Fetch S3 bucket name
fetch_s3_bucket

# Delete assets from S3 bucket
delete_from_s3

exit 0