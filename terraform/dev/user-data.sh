#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable Docker
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# Install tools
apt-get install -y git curl jq make htop

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Setup GitHub Actions Runner (if token provided)
if [ -n "${github_runner_token}" ]; then
    mkdir -p /home/ubuntu/actions-runner
    cd /home/ubuntu/actions-runner
    
    curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
        https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
    
    tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
    chown -R ubuntu:ubuntu /home/ubuntu/actions-runner
fi

# Create backup directory
mkdir -p /home/ubuntu/backups
chown ubuntu:ubuntu /home/ubuntu/backups

# Setup cron for backups (will be configured after repo clone)
echo "0 2 * * * /home/ubuntu/VMS/scripts/backup_db.sh >> /var/log/vms-backup.log 2>&1" | crontab -u ubuntu -

echo "Setup completed successfully"
