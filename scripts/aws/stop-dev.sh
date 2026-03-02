#!/bin/bash
set -e

INSTANCE_ID=$(terraform output -raw instance_id 2>/dev/null)

if [ -z "$INSTANCE_ID" ]; then
    echo "Error: Instance ID not found."
    exit 1
fi

echo "Stopping instance: $INSTANCE_ID"
aws ec2 stop-instances --instance-ids $INSTANCE_ID

echo "Waiting for instance to stop..."
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

echo ""
echo "✅ Instance stopped!"
echo "💰 You're now saving ~\$0.03/hour"
echo ""
echo "To start again: ./start-dev.sh"
