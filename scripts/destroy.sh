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

# ./delete-s3-react-app.sh

# Switch directories to deploy the AWS infrastrucutre"
(
  cd ../infra
  terraform init
  terraform plan
  terraform destroy -auto-approve
)
echo "Destroy done."