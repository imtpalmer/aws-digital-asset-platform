#!/bin/bash

set -e

# Define the root directories for lambdas, utils, and build
LAMBDA_DIR="/lambda-package/src"
UTILS_DIR="/lambda-package/src/utils"
BUILD_DIR="/lambda-package/build"

# Ensure the build directory exists and clean up any existing .zip files
mkdir -p "$BUILD_DIR"
rm -f "$BUILD_DIR"/*.zip

# Function to package a single Lambda
package_lambda() {
    local LAMBDA_PATH=$1
    local LAMBDA_NAME=$(basename "$LAMBDA_PATH" .py)  # Only the Python file name is used for packaging
    local TEMP_DIR=$(mktemp -d)

    echo "Packaging ${LAMBDA_NAME}..."

    # Copy the Lambda function and requirements.txt to the temp directory
    cp "$LAMBDA_PATH" "$TEMP_DIR/"
    if [ -f "$(dirname "$LAMBDA_PATH")/requirements.txt" ]; then
        cp "$(dirname "$LAMBDA_PATH")/requirements.txt" "$TEMP_DIR/"
    fi

    # Copy utility files (not the directory) into the temp directory
    if [ -d "$UTILS_DIR" ]; then
        cp "$UTILS_DIR"/* "$TEMP_DIR/"
    fi

    # Install dependencies in the temp directory
    if [ -f "$TEMP_DIR/requirements.txt" ]; then
        pip3 install -r "$TEMP_DIR/requirements.txt" -t "$TEMP_DIR/"
    fi

    cd "$TEMP_DIR"

    # Package the Lambda function into a zip file, excluding __pycache__
    zip -r9 "$BUILD_DIR/${LAMBDA_NAME}.zip" . -x "*/__pycache__/*"

    cd -
    # Clean up
    rm -rf "$TEMP_DIR"
}

# Find and package each Lambda function, ignoring the 'utils' folder
find "$LAMBDA_DIR" -path "$UTILS_DIR" -prune -o -maxdepth 3 -type f -name "*.py" -print | while IFS= read -r item; do
    package_lambda "$item"
done

echo "Lambdas packaged successfully."