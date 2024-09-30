#!/bin/bash

set -e

cd ../

# Set the name of the tar file (e.g., project_backup.tgz)
TAR_FILE="project_backup_$(date +%Y%m%d_%H%M%S).tgz"

# Create the tar archive while excluding files specified in .gitignore, common artifacts, and Terraform artifacts
tar --exclude-vcs \
    --exclude='node_modules' \
    --exclude='.DS_Store' \
    --exclude='.backups' \
    --exclude='*.log' \
    --exclude='coverage' \
    --exclude='*.swp' \
    --exclude='*.tmp' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='.idea' \
    --exclude='.vscode' \
    --exclude='.terraform' \
    --exclude='terraform.tfstate' \
    --exclude='terraform.tfstate.backup' \
    --exclude='.terraform.lock.hcl' \
    --exclude='*.tfplan' \
    -cvzf "$TAR_FILE" .

# Output the name of the tar file
echo "Created archive: $TAR_FILE"
