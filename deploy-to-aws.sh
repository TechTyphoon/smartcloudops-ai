#!/bin/bash
# SmartCloudOps AI - AWS Production Deployment Script
set -e

echo "🚀 SmartCloudOps AI - AWS Production Deployment"
echo "=============================================="

# Configuration
APP_SERVER="44.253.225.44"
MONITOR_SERVER="54.186.188.202"
KEY_PATH="$HOME/.ssh/smartcloudops-ai-key.pem"
PROJECT_NAME="smartcloudops-ai"

echo "📋 Deployment Configuration:"
echo "  Application Server: $APP_SERVER"
echo "  Monitoring Server: $MONITOR_SERVER"
echo "  SSH Key: $KEY_PATH"

# Wait for instances to be fully ready
echo -e "\n⏳ Waiting for instances to be fully ready..."
sleep 30

# Function to test SSH connectivity
test_ssh() {
    local host=$1
    local max_attempts=10
    local attempt=1
    
    echo "🔌 Testing SSH connectivity to $host..."
    while [ $attempt -le $max_attempts ]; do
        if timeout 10 ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -i $KEY_PATH ec2-user@$host "echo 'SSH Ready'" 2>/dev/null; then
            echo "✅ SSH connection to $host successful"
            return 0
        else
            echo "⏳ Attempt $attempt/$max_attempts failed, waiting 30s..."
            sleep 30
            ((attempt++))
        fi
    done
    echo "❌ SSH connection to $host failed after $max_attempts attempts"
    return 1
}

# Test SSH connectivity
if ! test_ssh $APP_SERVER; then
    echo "❌ Cannot connect to application server. Please check:"
    echo "  1. Security group allows SSH from your IP"
    echo "  2. Key file exists: $KEY_PATH"
    echo "  3. Instance is fully initialized"
    exit 1
fi

# Deploy application
echo -e "\n🚀 Deploying SmartCloudOps AI Application..."

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf smartcloudops-deploy.tar.gz \
    --exclude='*.git*' \
    --exclude='smartcloudops_env*' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='logs' \
    --exclude='terraform' \
    .

# Upload to application server
echo "⬆️ Uploading application to server..."
scp -i $KEY_PATH -o StrictHostKeyChecking=no smartcloudops-deploy.tar.gz ec2-user@$APP_SERVER:~/

# Install and start application
echo "🔧 Installing and starting application..."
ssh -i $KEY_PATH -o StrictHostKeyChecking=no ec2-user@$APP_SERVER << 'EOF'
    # Update system
    sudo yum update -y
    sudo yum install -y python3 python3-pip docker git htop

    # Extract application
    cd ~
    tar -xzf smartcloudops-deploy.tar.gz
    cd smartcloudops-ai* || cd .

    # Install Python dependencies
    python3 -m pip install --user -r requirements-production.txt

    # Start Docker services
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user

    # Start application with production settings
    export FLASK_ENV=production
    export DATABASE_URL="postgresql://smartcloudops:cloudops123@localhost:5432/smartcloudops_production"
    
    # Start services using Docker Compose
    sudo docker-compose -f docker-compose.production.yml up -d

    echo "✅ Application deployment complete!"
EOF

echo -e "\n🎯 Testing deployed application..."
sleep 10

# Test application endpoints
if timeout 30 curl -s http://$APP_SERVER:15000/health | grep -q "healthy"; then
    echo "✅ Application is responding on port 15000!"
else
    echo "⚠️ Application not yet responding, may need more time to start"
fi

# Cleanup
rm -f smartcloudops-deploy.tar.gz

echo -e "\n🎉 Deployment Complete!"
echo "================================"
echo "🌐 Application URL: http://$APP_SERVER:15000"
echo "📊 Monitoring: http://$MONITOR_SERVER:3000"
echo "🔐 Grafana Login: admin/SmartCloudOps2024!"
echo ""
echo "🔗 Next Steps:"
echo "  1. Access your application: http://$APP_SERVER:15000/demo"
echo "  2. Check health: http://$APP_SERVER:15000/health"
echo "  3. View monitoring: http://$MONITOR_SERVER:3000"
echo "  4. Set up SSL certificate for production"
echo ""
echo "📚 For troubleshooting, SSH to instances:"
echo "  ssh -i $KEY_PATH ec2-user@$APP_SERVER"
echo "  ssh -i $KEY_PATH ec2-user@$MONITOR_SERVER"
