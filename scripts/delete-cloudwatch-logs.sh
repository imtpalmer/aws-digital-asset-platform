#!/bin/bash

# Set the AWS region
REGION="us-east-1"

# Get all log groups
LOG_GROUPS=$(aws logs describe-log-groups --region $REGION --query "logGroups[*].logGroupName" --output text)

# Loop through and delete each log group
for LOG_GROUP in $LOG_GROUPS; do
    echo "Deleting log group: $LOG_GROUP"
    aws logs delete-log-group --log-group-name "$LOG_GROUP" --region $REGION
done

echo "All CloudWatch Log Groups deleted successfully."