#!/bin/bash
set -e

INSTANCE_ID=$(terraform output -raw instance_id 2>/dev/null)

if [ -z "$INSTANCE_ID" ]; then
    echo "Error: Instance ID not found. Run terraform apply first."
    exit 1
fi

echo "Starting instance: $INSTANCE_ID"
aws ec2 start-instances --instance-ids $INSTANCE_ID

echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

PUBLIC_IP=$(terraform output -raw public_ip)
echo ""
echo "✅ Instance started!"
echo "Public IP: $PUBLIC_IP"
echo "SSH: ssh -i vms-dev-key.pem ubuntu@$PUBLIC_IP"
