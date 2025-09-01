# 🔐 MCP Token Security Guide

## 🚨 **Critical Security Issue: Hardcoded Tokens**

Your current MCP configuration contains hardcoded API tokens which is a **major security risk**. This guide will help you secure your tokens while maintaining functionality.

## 📋 **Step-by-Step Security Implementation**

### **Step 1: Create Secure Environment File**

```bash
# Create a secure environment file (outside of git)
touch ~/.cursor/.env.mcp

# Set proper permissions
chmod 600 ~/.cursor/.env.mcp
```

### **Step 2: Add Your Tokens to Environment File**

Edit `~/.cursor/.env.mcp` and add:

```bash
# MCP Server Environment Variables
GITHUB_PERSONAL_ACCESS_TOKEN=<YOUR_GITHUB_PAT>
GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security
FIRECRAWL_API_KEY=<YOUR_FIRECRAWL_API_KEY>
AWS_REGION=us-west-2
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
POSTGRES_CONNECTION_STRING=postgresql+psycopg2://cloudops:cloudops@localhost:5432/cloudops
REDIS_URL=redis://localhost:6379
```

### **Step 3: Update MCP Configuration**

Replace your current `~/.cursor/mcp.json` with the secure template:

```json
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
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    }
    // ... other servers with environment variables
  }
}
```

### **Step 4: Update .gitignore**

Add these lines to your `.gitignore`:

```gitignore
# MCP Configuration and Secrets
~/.cursor/.env.mcp
~/.cursor/mcp.json
.cursor/.env.mcp
.cursor/mcp.json

# Environment files
.env
.env.local
.env.production
.env.staging

# Secrets and tokens
*.key
*.pem
*.p12
secrets/
```

## 🔄 **GitHub Integration: Safe Token Management**

### **Option 1: GitHub Secrets (Recommended for CI/CD)**

1. **Go to your GitHub repository**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add repository secrets:**

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=<YOUR_GITHUB_PAT>
FIRECRAWL_API_KEY=<YOUR_FIRECRAWL_API_KEY>
```

### **Option 2: GitHub Actions Workflow**

Create `.github/workflows/mcp-setup.yml`:

```yaml
name: MCP Token Setup

on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  setup-mcp:
    runs-on: ubuntu-latest
    steps:
      - name: Setup MCP Environment
        run: |
          echo "Setting up MCP environment variables..."
          echo "GITHUB_PERSONAL_ACCESS_TOKEN=${{ secrets.GITHUB_PERSONAL_ACCESS_TOKEN }}" >> $GITHUB_ENV
          echo "FIRECRAWL_API_KEY=${{ secrets.FIRECRAWL_API_KEY }}" >> $GITHUB_ENV
```

## 🛡️ **Security Best Practices**

### **1. Token Rotation**
- **Rotate tokens every 90 days**
- **Use different tokens for different environments**
- **Monitor token usage and access logs**

### **2. Access Control**
- **Limit token permissions to minimum required**
- **Use organization-level tokens when possible**
- **Implement IP whitelisting for API access**

### **3. Monitoring**
- **Set up alerts for unusual token usage**
- **Monitor GitHub audit logs**
- **Track API rate limits and usage**

### **4. Backup and Recovery**
- **Store token backups securely**
- **Document token recovery procedures**
- **Test token rotation procedures**

## 🔧 **Implementation Commands**

### **Quick Setup Script**

```bash
#!/bin/bash
# MCP Security Setup Script

echo "🔐 Setting up secure MCP configuration..."

# Create secure environment file
mkdir -p ~/.cursor
touch ~/.cursor/.env.mcp
chmod 600 ~/.cursor/.env.mcp

# Backup current configuration
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup

# Create secure configuration
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
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    }
  }
}
EOF

echo "✅ Secure MCP configuration created!"
echo "📝 Please add your tokens to ~/.cursor/.env.mcp"
echo "🔒 Remember to add ~/.cursor/.env.mcp to .gitignore"
```

## 🚨 **Emergency Procedures**

### **If Tokens Are Compromised:**

1. **Immediately revoke the exposed tokens**
2. **Generate new tokens**
3. **Update all environment files**
4. **Review access logs for unauthorized usage**
5. **Notify team members of the security incident**

### **Token Recovery:**

```bash
# GitHub Token Recovery
# 1. Go to GitHub Settings → Developer settings → Personal access tokens
# 2. Revoke compromised token
# 3. Generate new token with same permissions
# 4. Update ~/.cursor/.env.mcp

# Firecrawl Token Recovery
# 1. Contact Firecrawl support
# 2. Request token regeneration
# 3. Update environment variables
```

## ✅ **Verification Checklist**

- [ ] Environment file created with proper permissions
- [ ] MCP configuration updated to use environment variables
- [ ] .gitignore updated to exclude sensitive files
- [ ] GitHub secrets configured (if using CI/CD)
- [ ] Token permissions reviewed and minimized
- [ ] Backup procedures documented
- [ ] Team members notified of new procedures

## 📞 **Support and Resources**

- **GitHub Security**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure
- **Firecrawl Security**: Contact support for token management
- **MCP Documentation**: https://modelcontextprotocol.io/

---

**⚠️ Remember: Security is an ongoing process. Regularly review and update your security practices!**
