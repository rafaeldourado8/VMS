#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./setup_runner.sh <GITHUB_TOKEN>"
    echo ""
    echo "Get token from:"
    echo "GitHub → Settings → Actions → Runners → New self-hosted runner"
    exit 1
fi

GITHUB_TOKEN=$1
GITHUB_REPO="https://github.com/SEU_USUARIO/VMS"
RUNNER_VERSION="2.311.0"

echo "Setting up GitHub Actions Runner..."

# Create directory
mkdir -p /home/ubuntu/actions-runner
cd /home/ubuntu/actions-runner

# Download runner
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
    https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Configure
./config.sh --url $GITHUB_REPO --token $GITHUB_TOKEN --name vms-dev-runner --work _work --labels dev,self-hosted,linux

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start

echo "GitHub Actions Runner installed and started!"
echo "Check status: sudo ./svc.sh status"
