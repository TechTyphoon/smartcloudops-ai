#!/usr/bin/env python3
"""
Production Readiness Validation Script for Smart CloudOps AI
Phase 6.4: Production Readiness Validation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import requests
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check_docker_status():
    """Check if Docker containers are running properly."""
    print("🐳 Checking Docker container status...")

    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            containers = result.stdout.strip().split("\n")[1:]  # Skip header
            running_containers = [c for c in containers if c.strip()]

            if running_containers:
                print(f"✅ {len(running_containers)} containers running")
                for container in running_containers:
                    print(f"   {container}")
                return True
            else:
                print("⚠️  No containers running")
                return False
        else:
            print("❌ Docker command failed")
            return False
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
        return False


def check_flask_app():
    """Check if Flask application is responding."""
    print("🌐 Checking Flask application status...")

    try:
        # Check the correct port based on docker-compose configuration
        response = requests.get("http://localhost:3003/health", timeout=10)
        if response.status_code == 200:
            print("✅ Flask app responding on port 3003")
            return True
        else:
            print(f"⚠️  Flask app responding with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask app not responding: {e}")
        return False


def check_prometheus():
    """Check if Prometheus is accessible."""
    print("📊 Checking Prometheus status...")

    try:
        response = requests.get("http://localhost:9090/-/healthy", timeout=10)
        if response.status_code == 200:
            print("✅ Prometheus healthy on port 9090")
            return True
        else:
            print(f"⚠️  Prometheus responding with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Prometheus not accessible: {e}")
        return False


def check_grafana():
    """Check if Grafana is accessible."""
    print("📈 Checking Grafana status...")

    try:
        response = requests.get("http://localhost:3004/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Grafana healthy on port 3004")
            return True
        else:
            print(f"⚠️  Grafana responding with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Grafana not accessible: {e}")
        return False


def check_security_scan():
    """Run a quick security scan."""
    print("🔒 Running security scan...")

    try:
        # Check if bandit is available
        result = subprocess.run(["bandit", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Bandit security scanner available")

            # Run bandit on app directory
            result = subprocess.run(
                ["bandit", "-r", "app/", "-f", "json"], capture_output=True, text=True
            )

            if result.returncode == 0:
                try:
                    scan_results = json.loads(result.stdout)
                    issues = scan_results.get("results", [])

                    if not issues:
                        print("✅ No security issues found")
                        return True
                    else:
                        print(f"⚠️  Found {len(issues)} security issues")
                        for issue in issues[:3]:  # Show first 3
                            print(f"   {issue.get('issue_text', 'Unknown issue')}")
                        return False
                except json.JSONDecodeError:
                    print("⚠️  Could not parse security scan results")
                    return False
            else:
                print("⚠️  Security scan failed")
                return False
        else:
            print("⚠️  Bandit not available")
            return False
    except Exception as e:
        print(f"❌ Security scan failed: {e}")
        return False


def check_file_permissions():
    """Check critical file permissions."""
    print("📁 Checking file permissions...")

    critical_files = [
        "app/config.py",
        ".env",
        "docker-compose.yml",
        "terraform/main.tf",
    ]

    issues_found = 0

    for file_path in critical_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            mode = oct(stat.st_mode)[-3:]

            # Check if world-readable (should not be)
            if int(mode[2]) > 4:
                print(f"⚠️  {file_path}: {mode} (world-readable)")
                issues_found += 1
            else:
                print(f"✅ {file_path}: {mode}")
        else:
            print(f"⚠️  {file_path}: File not found")
            issues_found += 0

    return issues_found == 0


def check_dependencies():
    """Check if all dependencies are installed."""
    print("📦 Checking dependencies...")

    try:
        result = subprocess.run(["pip3", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            installed_packages = result.stdout.lower()

            required_packages = [
                "flask",
                "requests",
                "pyyaml",
                "scikit-learn",
                "pandas",
                "numpy",
                "prometheus-client",
            ]

            missing_packages = []
            for package in required_packages:
                if package not in installed_packages:
                    missing_packages.append(package)

            if not missing_packages:
                print("✅ All required packages installed")
                return True
            else:
                print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
                return False
        else:
            print("❌ Could not check dependencies")
            return False
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False


def generate_validation_report(results):
    """Generate a production readiness validation report."""
    print("\n📋 Generating Production Readiness Report...")

    report_file = (
        Path(__file__).parent.parent / "docs" / "PRODUCTION_READINESS_REPORT.md"
    )

    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    readiness_score = (passed_checks / total_checks) * 100

    status_emoji = (
        "✅" if readiness_score >= 80 else "⚠️" if readiness_score >= 60 else "❌"
    )

    report_content = f"""# Production Readiness Validation Report

**Validation Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Readiness Score**: {readiness_score:.1f}% {status_emoji}  
**Status**: {'Production Ready' if readiness_score >= 80 else 'Needs Attention' if readiness_score >= 60 else 'Not Ready'}

## 🎯 Validation Summary

**Total Checks**: {total_checks}  
**Passed**: {passed_checks}  
**Failed**: {total_checks - passed_checks}  
**Readiness Score**: {readiness_score:.1f}%

## 📊 Check Results

"""

    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        report_content += f"### {check_name}\n**Status**: {status}\n\n"

    report_content += f"""## 🚀 Production Readiness Assessment

**Current Status**: {status_emoji} {'Production Ready' if readiness_score >= 80 else 'Needs Attention' if readiness_score >= 60 else 'Not Ready'}

### Readiness Levels:
- **80-100%**: 🟢 Production Ready
- **60-79%**: 🟡 Needs Attention
- **0-59%**: 🔴 Not Ready

## 📋 Next Steps

"""

    if readiness_score >= 80:
        report_content += """✅ **System is production ready!**
- Proceed with production deployment
- Monitor system performance
- Document deployment procedures
"""
    elif readiness_score >= 60:
        report_content += """⚠️ **System needs attention before production**
- Address failed validation checks
- Re-run validation after fixes
- Consider staging deployment first
"""
    else:
        report_content += """❌ **System is not ready for production**
- Fix all critical issues
- Re-run comprehensive validation
- Do not deploy to production
"""

    report_content += f"""
## 🔧 Validation Details

This validation was performed using `scripts/production_validation.py` and covers:
- Docker container status
- Application health checks
- Monitoring system status
- Security scanning
- File permissions
- Dependency verification

---
**Generated by**: Smart CloudOps AI Production Validation Script  
**Phase**: 6.4 - Production Readiness Validation
"""

    with open(report_file, "w") as f:
        f.write(report_content)

    print(f"✅ Production readiness report generated: {report_file}")
    return report_file


def main():
    """Main function to run production readiness validation."""
    print("🚀 Starting Production Readiness Validation for Phase 6.4...")
    print("=" * 60)

    validation_results = {}

    # Run all validation checks
    validation_results["Docker Status"] = check_docker_status()
    validation_results["Flask Application"] = check_flask_app()
    validation_results["Prometheus Monitoring"] = check_prometheus()
    validation_results["Grafana Dashboard"] = check_grafana()
    validation_results["Security Scan"] = check_security_scan()
    validation_results["File Permissions"] = check_file_permissions()
    validation_results["Dependencies"] = check_dependencies()

    print("\n" + "=" * 60)

    # Calculate overall readiness
    total_checks = len(validation_results)
    passed_checks = sum(1 for result in validation_results.values() if result)
    readiness_score = (passed_checks / total_checks) * 100

    print(f"📊 VALIDATION RESULTS:")
    print(f"   Total Checks: {total_checks}")
    print(f"   Passed: {passed_checks}")
    print(f"   Failed: {total_checks - passed_checks}")
    print(f"   Readiness Score: {readiness_score:.1f}%")

    # Determine status
    if readiness_score >= 80:
        status = "🟢 PRODUCTION READY"
    elif readiness_score >= 60:
        status = "🟡 NEEDS ATTENTION"
    else:
        status = "🔴 NOT READY"

    print(f"   Status: {status}")

    # Generate report
    report_file = generate_validation_report(validation_results)

    print(f"\n🎉 Production readiness validation completed!")
    print(f"📋 Report generated: {report_file}")

    if readiness_score >= 80:
        print("🚀 System is ready for production deployment!")
    else:
        print("⚠️  Address failed checks before production deployment")

    return readiness_score >= 80


if __name__ == "__main__":
    main()
