#!/bin/bash

# 🔐 MCP Security Setup Script
# This script helps secure your MCP configuration by moving tokens to environment variables

set -e  # Exit on any error

echo "🔐 Setting up secure MCP configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Create .cursor directory if it doesn't exist
print_status "Creating .cursor directory..."
mkdir -p ~/.cursor

# Backup current configuration if it exists
if [[ -f ~/.cursor/mcp.json ]]; then
    print_status "Backing up current MCP configuration..."
    cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup.$(date +%Y%m%d_%H%M%S)
    print_success "Backup created: ~/.cursor/mcp.json.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create secure environment file
print_status "Creating secure environment file..."
touch ~/.cursor/.env.mcp
chmod 600 ~/.cursor/.env.mcp

# Add environment variables to .env.mcp
print_status "Adding environment variables to .env.mcp..."
cat > ~/.cursor/.env.mcp << 'EOF'
# MCP Server Environment Variables
# Store your sensitive tokens here - this file should NEVER be committed to git

# GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=<YOUR_GITHUB_PAT>
GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security

# Firecrawl Configuration
FIRECRAWL_API_KEY=<YOUR_FIRECRAWL_API_KEY>

# AWS Configuration
AWS_REGION=us-west-2

# Prometheus Configuration
PROMETHEUS_URL=http://localhost:9090

# Grafana Configuration
GRAFANA_URL=http://localhost:3000

# PostgreSQL Configuration
POSTGRES_CONNECTION_STRING=postgresql+psycopg2://cloudops:cloudops@localhost:5432/cloudops

# Redis Configuration
REDIS_URL=redis://localhost:6379
EOF

print_success "Environment file created: ~/.cursor/.env.mcp"

# Create secure MCP configuration
print_status "Creating secure MCP configuration..."
cat > ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e",
        "GITHUB_TOOLSETS",
        "ghcr.io/github/github-mcp-server",
        "stdio"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}",
        "GITHUB_TOOLSETS": "${GITHUB_TOOLSETS}"
      }
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@davenportsociety/clear-thought-patterns"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/reddy/Desktop"
      ]
    },
    "web-search": {
      "command": "npx",
      "args": [
        "-y",
        "duckduckgo-mcp-server"
      ]
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    },
    "aws": {
      "command": "npx",
      "args": ["-y", "@imazhar101/mcp-aws-server"],
      "env": {
        "AWS_REGION": "${AWS_REGION}"
      }
    },
    "kubernetes": {
      "command": "npx",
      "args": ["-y", "mcp-server-kubernetes"]
    },
    "terraform": {
      "command": "npx",
      "args": ["-y", "terraform-mcp-server"]
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "@0xshariq/docker-mcp-server"]
    },
    "prometheus": {
      "command": "npx",
      "args": ["-y", "prometheus-mcp"],
      "env": {
        "PROMETHEUS_URL": "${PROMETHEUS_URL}"
      }
    },
    "grafana": {
      "command": "npx",
      "args": ["-y", "grafana-mcp-analyzer"],
      "env": {
        "GRAFANA_URL": "${GRAFANA_URL}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@henkey/postgres-mcp-server"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    },
    "redis": {
      "command": "npx",
      "args": ["-y", "@pickstar-2002/redis-mcp"],
      "env": {
        "REDIS_URL": "${REDIS_URL}"
      }
    }
  }
}
EOF

print_success "Secure MCP configuration created: ~/.cursor/mcp.json"

# Update .gitignore if it exists
if [[ -f .gitignore ]]; then
    print_status "Updating .gitignore to exclude sensitive files..."
    
    # Check if entries already exist
    if ! grep -q "~/.cursor/.env.mcp" .gitignore; then
        echo "" >> .gitignore
        echo "# MCP Configuration and Secrets" >> .gitignore
        echo "~/.cursor/.env.mcp" >> .gitignore
        echo "~/.cursor/mcp.json" >> .gitignore
        echo ".cursor/.env.mcp" >> .gitignore
        echo ".cursor/mcp.json" >> .gitignore
        print_success ".gitignore updated"
    else
        print_warning ".gitignore already contains MCP entries"
    fi
else
    print_warning ".gitignore not found in current directory"
fi

# Create a source script for easy environment loading
print_status "Creating environment source script..."
cat > ~/.cursor/load-mcp-env.sh << 'EOF'
#!/bin/bash
# Source this script to load MCP environment variables

if [[ -f ~/.cursor/.env.mcp ]]; then
    export $(grep -v '^#' ~/.cursor/.env.mcp | xargs)
    echo "MCP environment variables loaded"
else
    echo "Error: ~/.cursor/.env.mcp not found"
    exit 1
fi
EOF

chmod +x ~/.cursor/load-mcp-env.sh
print_success "Environment loader created: ~/.cursor/load-mcp-env.sh"

# Display next steps
echo ""
print_success "✅ Secure MCP configuration setup complete!"
echo ""
print_status "Next steps:"
echo "1. Review and update tokens in ~/.cursor/.env.mcp if needed"
echo "2. Restart Cursor to load the new configuration"
echo "3. Test MCP functionality"
echo "4. Consider rotating your tokens for additional security"
echo ""
print_warning "Important: Keep ~/.cursor/.env.mcp secure and never commit it to git!"
echo ""

# Test if environment file is readable
if [[ -r ~/.cursor/.env.mcp ]]; then
    print_success "Environment file permissions are correct"
else
    print_error "Environment file permissions need adjustment"
    chmod 600 ~/.cursor/.env.mcp
fi

print_status "Setup complete! 🎉"

