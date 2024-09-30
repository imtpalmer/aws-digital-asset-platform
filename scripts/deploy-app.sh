#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the expected directory name
EXPECTED_DIR="scripts"

# Get the current working directory's base name
CURRENT_DIR=$(basename "$PWD")

# Check if the script is being run from the expected directory
if [ "$CURRENT_DIR" = "$EXPECTED_DIR" ]; then
  echo "Script is running from the $EXPECTED_DIR directory."
else
  echo "Script is NOT running from the $EXPECTED_DIR directory. Exiting."
  exit 1
fi

# Switch directories to deploy the AWS infrastrucutre"
(
  cd ../infra
  terraform init
  terraform plan
  # export TF_LOG=trace
  # export TF_LOG_PATH=terraform_trace.log
  terraform apply -auto-approve
  # build and deploy the react app assets to S3
  ../scripts/build-react-app.sh
)
echo "Deploy done."