# SmartCloudOps.AI Documentation

## 📚 Core Documentation

### Essential Guides
- [`GETTING_STARTED.md`](GETTING_STARTED.md) - Quick start guide for new users
- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Complete system architecture and design  
- [`API_REFERENCE.md`](API_REFERENCE.md) - Complete API documentation
- [`deployment-guide.md`](deployment-guide.md) - Production deployment instructions

### Development
- [`DEVELOPER_SETUP_GUIDE.md`](DEVELOPER_SETUP_GUIDE.md) - Local development environment setup
- [`SECURITY_HARDENING_GUIDE.md`](SECURITY_HARDENING_GUIDE.md) - Security best practices
- [`troubleshooting.md`](troubleshooting.md) - Common issues and solutions

## 🗃️ Archive

Historical documentation and development artifacts are preserved in:
- [`archive/phase-reports/`](archive/phase-reports/) - Development phase documentation
- [`archive/audits/`](archive/audits/) - Security audits and compliance reports  
- [`archive/presentations/`](archive/presentations/) - Business presentations and roadmaps

## 🚀 Quick Start

1. **New Users**: Start with [`GETTING_STARTED.md`](GETTING_STARTED.md)
2. **Developers**: Follow [`DEVELOPER_SETUP_GUIDE.md`](DEVELOPER_SETUP_GUIDE.md)  
3. **Architects**: Review [`ARCHITECTURE.md`](ARCHITECTURE.md)
4. **DevOps**: Use [`deployment-guide.md`](deployment-guide.md)

## 📋 Project Overview

SmartCloudOps.AI is an intelligent cloud operations platform providing:

- **🤖 AI-Powered Monitoring**: Predictive analytics and anomaly detection
- **🔧 Automated Remediation**: Self-healing infrastructure capabilities  
- **💬 ChatOps Integration**: Slack/Teams integration for operational workflows
- **🔐 Enterprise Security**: Multi-factor authentication and audit logging
- **☁️ Cloud-Native**: Kubernetes-ready with Terraform infrastructure-as-code

## 🔧 Configuration Quick Reference

- **Local Development**: Copy `env.template` to `.env`, use `docker-compose.yml`
- **Production**: Set environment variables via orchestrator/SSM
- **Terraform**: Uses remote state with `backend.hcl` configuration

---

**Last Updated**: August 16, 2025  
**Version**: v3.0.0
