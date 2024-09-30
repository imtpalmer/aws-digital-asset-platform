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

# Switch directories to run the native build of Python AWS lambdas in a Docker container
(
  cd ../lambdas
  # Define variables
  IMAGE_NAME="lambda-packager"
  CONTAINER_NAME="lambda-container"
  BUILD_DIR="$(pwd)/build"  # Adjusted build directory path to be within lambdas folder

  # Step 1: Ensure the build directory exists
  if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p "$BUILD_DIR"
    echo "Created build directory at $BUILD_DIR"
  else
    echo "Build directory already exists at $BUILD_DIR"
  fi

  # Step 2: Build the Docker image from the Dockerfile in the current directory
  echo "Building Docker image using Dockerfile in the current directory..."
  docker build --platform linux/amd64 -t $IMAGE_NAME .

  # Step 3: Run the Docker container to package the Lambdas
  echo "Running Docker container to package the Lambdas..."
  docker run --rm -v "$BUILD_DIR":/lambda-package/build --platform linux/amd64 $IMAGE_NAME

  # Step 4: Check if the ZIP files were created
  if ls "$BUILD_DIR"/*.zip 1>/dev/null 2>&1; then
    echo "Lambdas packaged successfully. Files are located in $BUILD_DIR:"
    ls "$BUILD_DIR"/*.zip
  else
    echo "Error: No .zip files were created."
    exit 1
  fi

  # Step 5: Clean up Docker image and related artifacts
  echo "Cleaning up Docker image and related artifacts..."
  docker rmi $IMAGE_NAME

  # Confirm the cleanup
  if [ "$(docker images -q $IMAGE_NAME 2>/dev/null)" == "" ]; then
    echo "Docker image $IMAGE_NAME removed successfully."
  else
    echo "Error: Docker image $IMAGE_NAME could not be removed."
    exit 1
  fi

  echo "Docker build and Lambda packaging process completed and cleaned up successfully."
)